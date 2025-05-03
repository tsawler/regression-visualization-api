from flask import Flask, request, jsonify
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
import io
import base64

app = Flask(__name__)

def encode_image():
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close()
    buf.seek(0)
    return base64.b64encode(buf.read()).decode('utf-8')

@app.route('/regression', methods=['POST'])
def regression():
    data = request.get_json()
    X = np.array(data['X'])
    y = np.array(data['y'])
    plot_type = data.get('plot', '2d')  # default to 2D

    model = LinearRegression()
    model.fit(X, y)

    if plot_type == '3d':
        if X.shape[1] != 2:
            return jsonify({'error': '3D plot requires exactly 2 features (columns) in X'}), 400

        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        ax.scatter(X[:, 0], X[:, 1], y, color='blue', label='Actual')

        # Predict surface
        x_surf, y_surf = np.meshgrid(
            np.linspace(X[:,0].min(), X[:,0].max(), 20),
            np.linspace(X[:,1].min(), X[:,1].max(), 20)
        )
        z_surf = model.predict(np.c_[x_surf.ravel(), y_surf.ravel()]).reshape(x_surf.shape)
        ax.plot_surface(x_surf, y_surf, z_surf, alpha=0.5, color='red')

        ax.set_xlabel("X1")
        ax.set_ylabel("X2")
        ax.set_zlabel("y")
    else:
        # 2D Plotting
        if X.shape[1] == 1:
            plt.scatter(X, y, color='blue', label='Actual')
            plt.plot(X, model.predict(X), color='red', label='Prediction')
            plt.xlabel("X")
            plt.ylabel("y")
        else:
            # For multiple regression, plot predicted vs actual
            y_pred = model.predict(X)
            plt.scatter(y, y_pred, color='green')
            plt.plot([y.min(), y.max()], [y.min(), y.max()], 'k--', lw=2)
            plt.xlabel("Actual y")
            plt.ylabel("Predicted y")
            plt.title("Actual vs Predicted")

    image_base64 = encode_image()
    return jsonify({'image_base64': image_base64})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
