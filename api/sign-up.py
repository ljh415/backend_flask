from flask import Flask, jsonify, request               # 1

app          = Flask(__name__)
app.users    = {}                                       # 2
app.id_count = 1                                        # 3

@app.route("/sign-up", methods=['POST'])                # 4
def sign_up():
    new_user                    = request.json          # 5
    new_user["id"]              = app.id_count          # 6
    app.users[app.id_count]     = new_user              # 7
    app.id_count                = app.id_count + 1      # 8

    return jsonify(new_user)                            # 9