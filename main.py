from flask import Flask, flash, request, redirect, url_for, render_template
import urllib.request
from PIL import Image, ImageTk, ImageFont, ImageDraw
import os
from werkzeug.utils import secure_filename
import glob

fnt = ImageFont.truetype('static/Fonts/Arial.ttf', 15)

UPLOAD_FOLDER = 'static/uploads/'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

app = Flask(__name__)
app.secret_key = "secret key"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
outfile = 'static/uploads/palette.png'


def save_palette(colors, swatchsize=400):
    num_colors = len(colors)
    palette = Image.new('RGB', (swatchsize*num_colors, swatchsize))
    draw = ImageDraw.Draw(palette)

    posx = 0
    for color in colors:
        draw.rounded_rectangle([posx, 0, posx+swatchsize, swatchsize], fill=color)
        posx = posx + swatchsize

    del draw
    palette.save(outfile, "PNG")


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def home_page():
    removing_files = glob.glob('static/uploads/*.png')
    for i in removing_files:
        os.remove(i)
    return render_template('index.html')


@app.route('/', methods=['POST'])
def upload_image():
    filename = ''
    removing_files = glob.glob('static/uploads/*.png')
    for i in removing_files:
        os.remove(i)

    if 'input_file' not in request.files:
        flash('No file part')
        return redirect(request.url)

    upload_file = request.files.getlist('input_file')

    if upload_file[0] and allowed_file(upload_file[0].filename):
        filename = secure_filename(upload_file[0].filename)
        upload_file[0].save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        img = Image.open(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        img = img.copy()

        # Reduce to palette
        paletted = img.convert('P', palette=Image.ADAPTIVE, colors=10)

        # Find dominant colors
        palette = paletted.getpalette()
        color_counts = sorted(paletted.getcolors(), reverse=True)
        colors = list()

        for i in range(10):
            palette_index = color_counts[i][1]
            dominant_color = palette[palette_index * 3:palette_index * 3 + 3]
            colors.append(tuple(dominant_color))

        save_palette(colors)
    return render_template('index.html', filename=filename)


@app.route('/display/<filename>')
def display_image(filename):
	return redirect(url_for('static', filename='uploads/' + filename), code=301)



# other way of running the flask application instead of running from terminal
if __name__ == "__main__":
    app.run(debug=True)

