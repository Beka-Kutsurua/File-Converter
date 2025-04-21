# conversion/routes.py
from conversion import app, db
from flask import Flask, render_template, redirect, url_for, flash, request, send_file, jsonify, send_from_directory, current_app
from flask_login import login_user, logout_user, login_required, current_user
from conversion.models import File, User
from conversion.forms import RegisterForm, LoginForm, DeleteForm
from werkzeug.utils import secure_filename
from io import BytesIO
import os
import tempfile
import zipfile
import traceback
from conversion.translate import translate
from conversion.scan import extract_text
from conversion.conversions import (
    copy_file,
    docx_to_pdf,
    pdf_to_docx,
    pdf_to_jpg, 
    pdf_to_png,
    images_to_pdf,
    jpg_to_png,
    png_to_jpg,
    pdf_to_pptx
)

conversion_options = {
    "docx-to-pdf": {
        "function": docx_to_pdf,
        "output_ext": ".pdf",
        "multiple_inputs": False,
        "multiple_outputs": False
    },
    "pdf-to-docx": {
        "function": pdf_to_docx,
        "output_ext": ".docx",
        "multiple_inputs": False,
        "multiple_outputs": False
    },
    "pdf-to-jpg": {
        "function": pdf_to_jpg,
        "output_ext": ".jpg",
        "multiple_inputs": False,
        "multiple_outputs": True
    },
    "pdf-to-png": {
        "function": pdf_to_png,
        "output_ext": ".png",
        "multiple_inputs": False,
        "multiple_outputs": True
    },
    "jpg-to-pdf": {
        "function": images_to_pdf,
        "output_ext": ".pdf",
        "multiple_inputs": True,
        "multiple_outputs": False
    },
    "png-to-pdf": {
        "function": images_to_pdf,
        "output_ext": ".pdf",
        "multiple_inputs": True,
        "multiple_outputs": False
    },
    "jpg-to-png": {
        "function": jpg_to_png,
        "output_ext": ".png",
        "multiple_inputs": True,
        "multiple_outputs": True
    },
    "png-to-jpg": {
        "function": png_to_jpg,
        "output_ext": ".jpg",
        "multiple_inputs": True,
        "multiple_outputs": True
    },
    "pdf-to-pptx": {
    "function": pdf_to_pptx,
    "output_ext": ".pptx",
    "multiple_inputs": False,
    "multiple_outputs": False
}
}


@app.route('/')
@app.route('/home')
def home_page():
    return render_template('home.html')


@app.route('/menu')
@login_required
def menu_page():
    return render_template('menu.html')


@app.route('/conversion', methods=['GET', 'POST'])
@login_required
def conversion_page():
    if request.method == 'POST':
        convert_type = request.form.get('convert_type')
        files = request.files.getlist('file')

        if not files or all(f.filename == '' for f in files):
            flash("No file(s) selected.", category='danger')
            return redirect(url_for('conversion_page'))

        option = conversion_options.get(convert_type)
        if option is None:
            flash("Unknown conversion type selected.", category='danger')
            return redirect(url_for('conversion_page'))

        file_root, _ = os.path.splitext(secure_filename(files[0].filename))
        output_filename = file_root + option['output_ext']
        output_path = os.path.join(app.config['CONVERTED_FOLDER'], output_filename)

        try:
            if option["multiple_inputs"]:
                input_paths = []
                for f in files:
                    filename = secure_filename(f.filename)
                    path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    f.save(path)
                    input_paths.append(path)

                output_files = option["function"](input_paths, app.config['CONVERTED_FOLDER'])

            else:
                uploaded_file = files[0]
                input_filename = secure_filename(uploaded_file.filename)
                input_path = os.path.join(app.config['UPLOAD_FOLDER'], input_filename)
                uploaded_file.save(input_path)

                output_files = option["function"](input_path, output_path)

                if isinstance(output_files, str):
                    output_files = [output_files]

            if option.get("multiple_outputs", False) and len(output_files) > 1:
                zip_filename = file_root + "_converted.zip"
                zip_path = os.path.join(app.config['CONVERTED_FOLDER'], zip_filename)

                with zipfile.ZipFile(zip_path, 'w') as zipf:
                    for f in output_files:
                        zipf.write(f, arcname=os.path.basename(f))

                input_file_path = input_paths[0] if option["multiple_inputs"] else input_path
                new_file_record = File(
                    convert_type=convert_type,
                    original_file=', '.join([f.filename for f in files]),
                    converted_file=zip_filename,
                    user_id=current_user.id,
                    original_data=open(input_file_path, 'rb').read(),
                    converted_data=open(zip_path, 'rb').read()
                )

                db.session.add(new_file_record)
                db.session.commit()

                return send_file(zip_path, as_attachment=True, download_name=zip_filename)

            # ✅ ONLY ONE OUTPUT FILE: send directly
            else:
                single_file_path = output_files[0]
                input_file_path = input_paths[0] if option["multiple_inputs"] else input_path
                new_file_record = File(
                    convert_type=convert_type,
                    original_file=files[0].filename,
                    converted_file=os.path.basename(single_file_path),
                    user_id=current_user.id,
                    original_data=open(input_file_path, 'rb').read(),
                    converted_data=open(single_file_path, 'rb').read()
                )

                db.session.add(new_file_record)
                db.session.commit()

                return send_file(single_file_path, as_attachment=True, download_name=os.path.basename(single_file_path))

        except Exception as e:
            print(traceback.format_exc())
            flash(f"Conversion error: {str(e) or 'Check console for details.'}", category='danger')
            return redirect(url_for('conversion_page'))

    files = File.query.filter_by(user_id=current_user.id).all()
    return render_template('conversion.html', files=files)



@app.route('/history', methods=['GET', 'POST'])
@login_required
def history_page():
    if request.method == 'POST':
        if 'delete_item' in request.form:
            item_to_delete = request.form.get('delete_item')
            item_to_delete_object = File.query.filter_by(original_file=item_to_delete, user_id=current_user.id).first()
            if item_to_delete_object:
                item_to_delete_object.delete()
                flash(f"File '{item_to_delete_object.converted_file}' has been deleted.", category='success')
            else:
                flash("File could not be deleted.", category='danger')
            return redirect(url_for('history_page'))

        elif 'download_file_id' in request.form:
            file_id = request.form.get('download_file_id')
            file_type = request.form.get('file_type')

            file_obj = File.query.filter_by(id=file_id, user_id=current_user.id).first()
            if not file_obj:
                flash("File not found or unauthorized.", category="danger")
                return redirect(url_for('history_page'))

            if file_type == "original":
                file_data = file_obj.original_data
                filename = file_obj.original_file
            else:
                file_data = file_obj.converted_data
                filename = file_obj.converted_file

            return send_file(BytesIO(file_data),
                             as_attachment=True,
                             download_name=filename,
                             mimetype='application/octet-stream')

    files = File.query.filter_by(user_id=current_user.id).order_by(File.timestamp.desc()).all()
    return render_template('history.html', files=files)

@app.route('/translate', methods=['GET', 'POST'])
@login_required
def translate_page():
    translated_text = None
    if request.method == 'POST':
        input_text = request.form.get('input_text', '')
        translated_text = translate(input_text)
    return render_template('translate.html', translated_text=translated_text)

from flask import request, jsonify

@app.route('/translate-api', methods=['POST'])
@login_required
def translate_api():
    data = request.get_json()
    input_text = data.get("input_text", "")
    translated = translate(input_text)
    return jsonify({"translated_text": translated})

@app.route('/scan', methods=['GET', 'POST'])  # ✅ Add POST
@login_required
def scan_page():
    extracted_text = None

    if request.method == 'POST':
        if 'image' not in request.files or request.files['image'].filename == '':
            flash("No image selected.", category='danger')
            return render_template('scan.html', extracted_text=extracted_text)

        image_file = request.files['image']
        filename = secure_filename(image_file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        image_file.save(filepath)

        extracted_text = extract_text(filepath)

    return render_template('scan.html', extracted_text=extracted_text)

@app.route('/register', methods=['GET', 'POST'])
def register_page():
    form = RegisterForm()
    if form.validate_on_submit():
        user_to_create = User(
            username=form.username.data,
            email_adress=form.email_adress.data,
            password=form.password1.data
        )
        db.session.add(user_to_create)
        db.session.commit()
        login_user(user_to_create)
        flash(f'Account created successfully! You are now logged in as {user_to_create.username}', category='success')
        return redirect(url_for('menu_page'))

    if form.errors != {}:
        for err_msg in form.errors.values():
            flash(f'There was an error with creating a user: {err_msg}', category='danger')
    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login_page():
    form = LoginForm()
    if form.validate_on_submit():
        attempted_user = User.query.filter_by(username=form.username.data).first()
        if attempted_user and attempted_user.check_password_correction(
                attempted_password=form.password.data):
            login_user(attempted_user)
            flash(f'Success! You are logged in as: {attempted_user.username}', category='success')
            return redirect(url_for('menu_page'))
        else:
            flash('Username and password do not match! Please try again.', category='danger')

    return render_template('login.html', form=form)

@app.route('/logout')
def logout_page():
    logout_user()
    flash('You have been logged out!', category='info')
    return redirect(url_for('home_page'))
