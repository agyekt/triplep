

def admin_exists(username, email):
    return Admin.query.filter_by(username=username).first() or Admin.query.filter_by(email=email).first()


def create_admin_if_not_exists():
    username = "admin"
    email = "admin@gmail.com"
    password = "admin"
    if not admin_exists(username, email):
        new_admin = Admin(username=username, email=email, password=password)
        db.session.add(new_admin)
        db.session.commit()