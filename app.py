from flask import Flask, request, jsonify
import numpy as np
from sklearn.linear_model import LinearRegression
import plotly.graph_objs as go
import json

# Initialize the Flask application
app = Flask(__name__)


@app.route('/', methods=['POST'])
def regression():
    """
    Endpoint to perform linear regression and return a complete interactive Plotly HTML page
    with Bootstrap 5 styling.
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

    # Set default layout for better visibility
    default_layout = {
        "height": 800,
        "width": 1000,
        "autosize": True,
        "margin": {"l": 80, "r": 80, "b": 80, "t": 100, "pad": 4}
    }

    # Extract custom layout settings if provided, otherwise use defaults
    custom_layout = data.get('layout', default_layout)

    # Ensure minimum size for visibility
    if 'height' not in custom_layout:
        custom_layout['height'] = 800
    if 'width' not in custom_layout:
        custom_layout['width'] = 1000

    model = LinearRegression()
    model.fit(X, y)

    # Prepare data for plotting
    plot_data = []
    layout_obj = {}

    if plot_type == '3d':
        if X.shape[1] != 2:
            return jsonify({'error': '3D plot requires exactly 2 features (columns) in X'}), 400

        # Create surface grid
        x_surf, y_surf = np.meshgrid(
            np.linspace(X[:, 0].min(), X[:, 0].max(), 20),
            np.linspace(X[:, 1].min(), X[:, 1].max(), 20)
        )
        z_surf = model.predict(
            np.c_[x_surf.ravel(), y_surf.ravel()]).reshape(x_surf.shape)

        # Create 3D scatter for data points
        scatter_data = {
            'type': 'scatter3d',
            'x': X[:, 0].tolist(),
            'y': X[:, 1].tolist(),
            'z': y.tolist(),
            'mode': 'markers',
            'marker': {
                'size': 8,
                'color': 'blue',
                'opacity': 0.8
            },
            'name': 'Actual Data'
        }
        plot_data.append(scatter_data)

        # Create surface for regression plane
        surface_data = {
            'type': 'surface',
            'x': x_surf.tolist(),
            'y': y_surf.tolist(),
            'z': z_surf.tolist(),
            'opacity': 0.7,
            'colorscale': 'Reds',
            'showscale': False,  # Hide the color bar
            'name': 'Regression Surface'
        }
        plot_data.append(surface_data)

        # Layout for 3D plot - FIXED TO USE CUSTOM LAYOUT VALUES
        layout_obj = {
            'title': title or '3D Linear Regression',
            'scene': {
                'xaxis': {'title': x_label or 'Feature 1'},
                'yaxis': {'title': y_label or 'Feature 2'},
                'zaxis': {'title': z_label or 'Target'}
            },
            'height': custom_layout.get('height', 800),
            'width': custom_layout.get('width', 1000),
            'autosize': custom_layout.get('autosize', True),
            'margin': custom_layout.get('margin', {'l': 0, 'r': 0, 'b': 0, 't': 50})
        }

    else:
        if X.shape[1] == 1:
            # For simple 2D regression
            x_vals = X.flatten().tolist()
            y_vals = y.tolist()
            y_pred = model.predict(X).tolist()

            actual_data = {
                'type': 'scatter',
                'x': x_vals,
                'y': y_vals,
                'mode': 'markers',
                'marker': {'color': 'blue', 'size': 10},
                'name': 'Actual'
            }
            plot_data.append(actual_data)

            pred_data = {
                'type': 'scatter',
                'x': x_vals,
                'y': y_pred,
                'mode': 'lines',
                'line': {'color': 'red', 'width': 3},
                'name': 'Prediction'
            }
            plot_data.append(pred_data)

            layout_obj = {
                'title': title or '2D Linear Regression',
                'xaxis': {'title': x_label or 'X'},
                'yaxis': {'title': y_label or 'y'},
                'height': custom_layout.get('height', 800),
                'width': custom_layout.get('width', 1000),
                'autosize': custom_layout.get('autosize', True),
                'margin': custom_layout.get('margin', {'l': 80, 'r': 80, 'b': 80, 't': 100})
            }
        else:
            # For multi-feature regression: actual vs predicted
            y_pred = model.predict(X).tolist()

            scatter_data = {
                'type': 'scatter',
                'x': y.tolist(),
                'y': y_pred,
                'mode': 'markers',
                'marker': {'color': 'green', 'size': 10},
                'name': 'Actual vs Predicted'
            }
            plot_data.append(scatter_data)

            min_val = min(min(y), min(y_pred))
            max_val = max(max(y), max(y_pred))

            line_data = {
                'type': 'scatter',
                'x': [min_val, max_val],
                'y': [min_val, max_val],
                'mode': 'lines',
                'line': {'dash': 'dash', 'color': 'black'},
                'name': 'Perfect Prediction'
            }
            plot_data.append(line_data)

            layout_obj = {
                'title': title or 'Actual vs Predicted',
                'xaxis': {'title': x_label or 'Actual y'},
                'yaxis': {'title': y_label or 'Predicted y'},
                'height': custom_layout.get('height', 800),
                'width': custom_layout.get('width', 1000),
                'autosize': custom_layout.get('autosize', True),
                'margin': custom_layout.get('margin', {'l': 80, 'r': 80, 'b': 80, 't': 100})
            }

    # Convert the data to JSON
    plot_data_json = json.dumps(plot_data)
    layout_json = json.dumps(layout_obj)

    # Create a complete standalone HTML page with Bootstrap 5 styling
    html = f'''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title or 'Regression Analysis'}</title>
    <!-- Plotly JS -->
    <script src="https://cdn.plot.ly/plotly-3.0.1.min.js" charset="utf-8"></script>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
        }}
        .container {{
            width: 100%;
            max-width: 1200px;
            margin: 0 auto;
            padding: 1rem;
        }}
        .title {{
            text-align: center;
            margin-bottom: 1rem;
        }}
        .plot-container {{
            height: {custom_layout.get('height')}px;
            min-height: 600px;
            width: 100%;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1 class="title">{title or 'Regression Analysis'}</h1>
        <div id="plot" class="plot-container"></div>
    </div>
    
    <script>
        // Define the data
        const data = {plot_data_json};
        
        // Define the layout with responsive settings
        const layout = {layout_json};
        layout.autosize = true;
        
        // Create the plot with modebar always visible
        document.addEventListener('DOMContentLoaded', function() {{
            Plotly.newPlot('plot', data, layout, {{
                responsive: true,
                displayModeBar: true,
                displaylogo: false
            }});
            
            // Handle window resize to make the chart responsive
            window.addEventListener('resize', function() {{
                Plotly.relayout('plot', {{
                    'width': document.getElementById('plot').offsetWidth
                }});
            }});
        }});
    </script>
</body>
</html>
'''

    print(f"Generated HTML with length: {len(html)}")

    return jsonify({'html': html})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)