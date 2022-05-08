import requests
from flask import Flask, request, jsonify, Response
from http import HTTPStatus
from faker import Faker
import pandas as pd
import csv


app = Flask(__name__, static_url_path='/static')


@app.errorhandler(HTTPStatus.UNPROCESSABLE_ENTITY)
@app.errorhandler(HTTPStatus.BAD_REQUEST)
def error_handling(error):
    headers = error.data.get("headers", None)
    messages = error.data.get("messages", ["Invalid request."])

    if headers:
        return jsonify(
            {
                'errors': messages
            },
            error.code,
            headers
        )
    else:
        return jsonify(
            {
                'errors': messages
            },
            error.code,
        )


@app.route("/bitcoin_rate")
def get_bitcoin_rate():
    currency_rate = ''
    url = "https://bitpay.com/api/rates"
    result = requests.get(url, {})
    if result.status_code not in (HTTPStatus.OK,):
        return Response("ERROR: Something went wrong",
                        status=result.status_code)
    else:
        result = result.json()

    cur_arg = request.args.get('currency')
    if cur_arg:
        currency = cur_arg
    else:
        currency = 'USD'

    for cur in result:
        if cur['code'] == currency:
            currency_rate = cur['rate']

    if currency_rate:
        return f'Bitcoin_value is {currency_rate} {currency}'
    else:
        return 'Sorry, such currency do not exist)'

#app.run(debug=True, port=5000)


@app.route("/generate_students")
def generate_students():
    try:
        count = int(request.args.get('count'))
        if count > 1000 or count <= 0:
            return "Maximum amount of students is 1000!"
    except TypeError:
        return "There is no argument in your request!"
    fake = Faker('UK')
    with open('static/students.csv', 'w', encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['First_name', 'Last_name', 'email', 'password', 'birthday'])
        for _ in range(count):
            writer.writerow([fake.first_name(), fake.last_name(), fake.email(), fake.password(),
                             fake.date_of_birth(minimum_age=18, maximum_age=45)])
    data = pd.read_csv('static/students.csv')
    return data.to_html()


app.run(debug=True, port=5000)

