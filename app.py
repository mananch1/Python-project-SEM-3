from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # Placeholder for authentication logic
        if username == 'admin' and password == '1234':
            return redirect(url_for('atm',auth=1))
        else:
            error = 'Invalid Credentials. Please try again.'
            return render_template('login.html', error=error)
    return render_template('login.html')

@app.route('/atm')
def atm():
    auth = request.args.get('auth', type=int)
    if(auth!=1):
        return redirect(url_for('login'))
    return render_template('atm.html')

if __name__ == '__main__':
    app.run(debug=True)
