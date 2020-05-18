import os
import time
from flask import Flask, redirect, url_for, request, jsonify
import Face


app = Flask(__name__)

@app.route("/", methods=['GET', 'POST'])
def index():
    if request.method == 'POST' and request.headers['Content-Type'] == 'application/octet-stream':
        try:
            image = open('./images/image.jpg', 'wb')
            image.write(request.data)
            image.close()
            image = open('./images/image.jpg', 'rb')
            response = Face.who_is_it(image)
            image.close()
            if isinstance(response, dict):
                if 0 in response:
                    name = response[0]['Date'] + '-' + response[0]['Time'] + '-' + response[0]['Name']
                    name = name.replace("/", "")
                    name = name.replace(":", "")
                    os.rename('./images/image.jpg', './images/' + name + '.jpg')
                    print(response)
                    return jsonify(response)
            return {0 : 'Error'}
        except FileNotFoundError as error:
            print(error)
            return {0 : 'FileNotFoundError'}
        except FileExistsError as error:
            print(error)
            return {0 : 'FileExistsError'}
        except PermissionError as error:
            print(error)
            return {0 : 'PermissionError'}
    else:
        return redirect(url_for('static', filename='index.html'))

@app.route("/add", methods=['GET', 'POST'])
def addnew():
    if request.method == 'POST' and request.headers['Content-Type'] == 'application/octet-stream' and request.headers['Name'] != '':
        try:
            image = open('./images/image.jpg', 'wb')
            image.write(request.data)
            image.close()
            image = open('./images/image.jpg', 'rb')
            response = Face.who_is_it(image)
            image.close()
            if isinstance(response, dict):
                if 0 in response and response[0]['Name'] == 'Unknown':
                    name = response[0]['Date'] + '-' + response[0]['Time'] + '-' + request.headers['Name']
                    name = name.replace("/", "")
                    name = name.replace(":", "")
                    os.rename('./images/image.jpg', './images/' + name + '.jpg')
                    time.sleep(1)
                    image = open('./images/' + name + '.jpg', 'rb')
                    result = {0 : {'Status' : Face.add_new(image, name=request.headers['Name'])}}
                    image.close()
                    print(result)
                    return jsonify(result)

                elif 0 in response and response[0]['Name'] == request.headers['Name']:
                    name = response[0]['Date'] + '-' + response[0]['Time'] + '-' + request.headers['Name']
                    name = name.replace("/", "")
                    name = name.replace(":", "")
                    os.rename('./images/image.jpg', './images/' + name + '.jpg')
                    time.sleep(1)
                    image = open('./images/' + name + '.jpg', 'rb')
                    result = {0 : {'Status' : Face.add_new(image, human_id=response[0]['Person ID'])}}
                    image.close()
                    print(result)
                    return jsonify(result)

                elif 0 in response and response[0]['Name'] != request.headers['Name']:
                    name = response[0]['Date'] + '-' + response[0]['Time'] + '-' + request.headers['Name']
                    name = name.replace("/", "")
                    name = name.replace(":", "")
                    os.rename('./images/image.jpg', './images/' + name + '.jpg')
                    time.sleep(1)
                    image = open('./images/' + name + '.jpg', 'rb')
                    result = {0 : {'Status' : Face.add_new(image, name=request.headers['Name'], human_id=response[0]['Person ID'])}}
                    image.close()
                    print(result)
                    return jsonify(result)

            return {0 : 'Error'}
        except FileNotFoundError as error:
            print(error)
            return {0 : 'FileNotFoundError'}
        except FileExistsError as error:
            print(error)
            return {0 : 'FileExistsError'}
        except PermissionError as error:
            print(error)
            return {0 : 'PermissionError'}
    else:
        return redirect(url_for('static', filename='add.html'))

@app.route("/api/log", methods=['GET'])
def log_route():
    name_list = []
    folder_content = os.listdir('./images')
    folder_content.sort()
    for item in folder_content:
        if len(item.split('-')) == 3:
            name_in_file = item.split('-')[2].split('.')[0]
            date_in_file = item.split('-')[0]
            time_in_file = item.split('-')[1]
            if name_in_file != "Unknown":
                name_list.append({'name' : name_in_file, 'date' : date_in_file, 'time' : time_in_file})

    return jsonify({'data' : name_list})
