from flask import Flask, request, jsonify
import numpy as np
from sklearn.linear_model import LinearRegression
import plotly.graph_objs as go
import plotly.io as pio

# Initialize the Flask application
app = Flask(__name__)


@app.route('/regression', methods=['POST'])
def regression():
    """
    Endpoint to perform linear regression and return an interactive Plotly visualization.

    Expected JSON format:
    {
        "X": [[x1_1, x1_2, ...], [x2_1, x2_2, ...], ...],
        "y": [y1, y2, ...],
        "plot": "2d" or "3d",  # Optional, defaults to '2d'
        "labels": {
            "title": "...",
            "x_label": "...",
            "y_label": "...",
            "z_label": "..."  # Only for 3D
        }
    }

    Returns:
        JSON with 'html' key containing interactive Plotly HTML (to embed in frontend).
    """
    data = request.get_json()

    X = np.array(data['X'])
    y = np.array(data['y'])
    plot_type = data.get('plot', '2d')

    labels = data.get('labels', {})
    title = labels.get('title', '')
    x_label = labels.get('x_label', '')
    y_label = labels.get('y_label', '')
    z_label = labels.get('z_label', '')

    model = LinearRegression()
    model.fit(X, y)

    if plot_type == '3d':
        if X.shape[1] != 2:
            return jsonify({'error': '3D plot requires exactly 2 features (columns) in X'}), 400

        # Create surface grid
        x_surf, y_surf = np.meshgrid(
            np.linspace(X[:, 0].min(), X[:, 0].max(), 20),
            np.linspace(X[:, 1].min(), X[:, 1].max(), 20)
        )
        z_surf = model.predict(np.c_[x_surf.ravel(), y_surf.ravel()]).reshape(x_surf.shape)

        # Create 3D scatter and surface plot
        scatter = go.Scatter3d(
            x=X[:, 0], y=X[:, 1], z=y,
            mode='markers',
            marker=dict(size=4, color='blue'),
            name='Actual'
        )

        surface = go.Surface(
            x=x_surf, y=y_surf, z=z_surf,
            opacity=0.5,
            colorscale='Reds',
            name='Prediction Surface'
        )

        layout = go.Layout(
            title=title or '3D Linear Regression',
            scene=dict(
                xaxis_title=x_label or 'X1',
                yaxis_title=y_label or 'X2',
                zaxis_title=z_label or 'y'
            )
        )

        fig = go.Figure(data=[scatter, surface], layout=layout)

    else:
        if X.shape[1] == 1:
            # Simple 2D regression
            x_vals = X.flatten()
            y_pred = model.predict(X)

            trace_actual = go.Scatter(
                x=x_vals, y=y,
                mode='markers',
                marker=dict(color='blue'),
                name='Actual'
            )
            trace_pred = go.Scatter(
                x=x_vals, y=y_pred,
                mode='lines',
                line=dict(color='red'),
                name='Prediction'
            )

            layout = go.Layout(
                title=title or '2D Linear Regression',
                xaxis=dict(title=x_label or 'X'),
                yaxis=dict(title=y_label or 'y')
            )

            fig = go.Figure(data=[trace_actual, trace_pred], layout=layout)

        else:
            # Multi-feature regression: actual vs predicted
            y_pred = model.predict(X)

            trace = go.Scatter(
                x=y, y=y_pred,
                mode='markers',
                marker=dict(color='green'),
                name='Actual vs Predicted'
            )

            line = go.Scatter(
                x=[y.min(), y.max()], y=[y.min(), y.max()],
                mode='lines',
                line=dict(dash='dash', color='black'),
                name='Perfect Prediction'
            )

            layout = go.Layout(
                title=title or 'Actual vs Predicted',
                xaxis=dict(title=x_label or 'Actual y'),
                yaxis=dict(title=y_label or 'Predicted y')
            )

            fig = go.Figure(data=[trace, line], layout=layout)

    # Convert to interactive HTML snippet (can be embedded in frontend)
    html = pio.to_html(fig, full_html=False)

    return jsonify({'html': html})


# Run the application if this file is executed directly
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
