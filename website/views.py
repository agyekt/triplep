from flask import Blueprint, render_template, request, flash, jsonify,redirect
from flask_login import login_required, current_user
from .models import Urls,url_analytics,click_counts
from . import db
import json
import string
import random
import qrcode
import base64
from io import BytesIO
import requests

views = Blueprint('views', __name__)


@views.route('/', methods=['GET', 'POST'])
def home():
    return render_template("home.html", user=current_user)


@views.route('/about')
def about():
    return render_template("about.html")

@views.route('/features')
def features():
    return render_template("features.html")

@views.route('/faq')
def faq():
    print("Current User after login:", current_user) 
    return render_template("faq.html")

@views.route('/contact')
def contact():
    return render_template("contact.html")

def generate_short_url():
    characters = string.ascii_uppercase + string.digits
    return ''.join(random.choices(characters, k=6))

@views.route('/shorten-url', methods=['GET', 'POST'])
@login_required
def shorten_url():
    if request.method == 'POST':
        long_url = request.form['long_url']
        short_url = generate_short_url()
        short_url = "http://127.0.0.1:5000/" + short_url
        userid = current_user.id
        new_url = Urls(user_id=userid,original_url=long_url,shorten_url=short_url)
        db.session.add(new_url)
        db.session.commit()      

        return render_template('dashboard.html', short_url=short_url)

    return render_template('dashboard.html')

@views.route('/generate_qr', methods=['GET', 'POST'])
@login_required
def generate_qr():
    if request.method == 'POST':
        url = request.form['url']
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(url)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        img_bytes = BytesIO()
        img.save(img_bytes)
        img_bytes = base64.b64encode(img_bytes.getvalue()).decode()

        return render_template('dashboard.html', qr_code=img_bytes)
    return render_template('dashboard.html')  

@views.route('/history')
@login_required
def hist():
    userid = current_user.id
    urls = db.session.query(Urls.original_url,Urls.shorten_url).filter(Urls.user_id == userid).all()
    return render_template('history.html',urls=urls)


@views.route('/url_analytics')
@login_required
def url_ana():
    url_name = request.args.get('url')
    result = db.session.query(Urls.id).filter(Urls.shorten_url == url_name).first()
    url_id =result[0]
    analy_data = db.session.query(url_analytics.ipaddress,url_analytics.city,url_analytics.country,url_analytics.click_date).filter(url_analytics.url_id == url_id).all()
    click_num = db.session.query(click_counts.click_num).filter(click_counts.url_id == url_id).first()
    try:
        click_num = click_num[0]
        print(analy_data)
        return render_template("url_analytics.html",analy_data=analy_data,click_num=click_num,session=len(analy_data))
    except:
        analy_data = []
        return render_template("url_analytics.html",analy_data=analy_data,click_num=0,session=0)


@views.route('/<short_url>')
def redirect_to_url(short_url):
    short_url = "http://127.0.0.1:5000/" + short_url
    result = db.session.query(Urls.original_url,Urls.id).filter(Urls.shorten_url == short_url).first()

    if result:
        url_id =result[1]
        ip_addr = request.remote_addr
        url = "https://ipgeolocation.abstractapi.com/v1/?api_key=fe808d879f5044d6b0169d1fe7dff300&ip_address="+ip_addr
        response = requests.get(url)
        print(response.text)
        city = response.text
        city = city.split('"city":')[1].split(',')[0]
        country = response.text
        country = country.split('"country":')[1].split(',')[0]
        print('ip address',ip_addr,city,country)
        city = "yangon"
        country = "myanmar"
        print(url_id,ip_addr)
        uniq_visitor = db.session.query(url_analytics.ipaddress) \
        .filter(url_analytics.ipaddress == ip_addr) \
        .filter(url_analytics.url_id == url_id) \
        .first()
        print(uniq_visitor)
        if not uniq_visitor:
            new_visitor = url_analytics(ipaddress=ip_addr,city=city, country=country,url_id=url_id)
            db.session.add(new_visitor)
            db.session.commit()
            try:
                click_num = db.session.query(click_counts.click_num).filter(click_counts.url_id == url_id).first()
                clicks = int(click_num[0]) + 1
            except:
                clicks = 1
            new_clicker = click_counts(click_num=clicks,url_id=url_id)
            existing_clicker = db.session.query(click_counts).filter_by(url_id=url_id).first()

            if existing_clicker:
                existing_clicker.click_num = clicks
                db.session.merge(existing_clicker)
            else:
                db.session.add(new_clicker)

            db.session.commit()
        else:
            try:
                click_num = db.session.query(click_counts.click_num).filter(click_counts.url_id == url_id).first()
                clicks = int(click_num[0]) + 1
            except:
                clicks = 1
            new_clicker = click_counts(click_num=clicks,url_id=url_id)
            existing_clicker = db.session.query(click_counts).filter_by(url_id=url_id).first()

            if existing_clicker:
                existing_clicker.click_num = clicks
                db.session.merge(existing_clicker)
            else:
                db.session.add(new_clicker)

            db.session.commit()
        return redirect(result[0])
    else:
        return render_template("404.html")

