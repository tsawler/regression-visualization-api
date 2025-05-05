from flask import Flask, request, jsonify
import numpy as np
from sklearn.linear_model import LinearRegression
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize the Flask application
app = Flask(__name__)


@app.route('/', methods=['POST'])
def regression():
    """
    Endpoint to perform linear regression and return a complete interactive Plotly HTML page.
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
        # Increased margins for axis labels
        "margin": {"l": 120, "r": 80, "b": 120, "t": 100, "pad": 10}
    }

    # Extract custom layout settings if provided, otherwise use defaults
    custom_layout = data.get('layout', default_layout)

    # Ensure minimum margin sizes for visibility of axis labels
    if 'margin' not in custom_layout:
        custom_layout['margin'] = default_layout['margin']
    else:
        # Ensure minimum margins for axis labels
        margin = custom_layout['margin']
        if 'l' not in margin or margin['l'] < 120:
            margin['l'] = 120
        if 'b' not in margin or margin['b'] < 120:
            margin['b'] = 120
        if 'pad' not in margin:
            margin['pad'] = 10

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

        # Layout for 3D plot with improved axis settings - updated for Plotly.js 3.0+
        layout_obj = {
            'title': {'text': title or '3D Linear Regression'},
            'scene': {
                'xaxis': {
                    'title': {'text': x_label or 'Feature 1', 'font': {'size': 16}},
                    'showgrid': True,
                    'showline': True
                },
                'yaxis': {
                    'title': {'text': y_label or 'Feature 2', 'font': {'size': 16}},
                    'showgrid': True,
                    'showline': True
                },
                'zaxis': {
                    'title': {'text': z_label or 'Target', 'font': {'size': 16}},
                    'showgrid': True,
                    'showline': True
                }
            },
            'height': custom_layout.get('height', 800),
            'width': custom_layout.get('width', 1000),
            'autosize': custom_layout.get('autosize', True),
            'margin': custom_layout.get('margin', {'l': 120, 'r': 80, 'b': 120, 't': 100, 'pad': 10})
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

            # Improved 2D layout with better axis visibility - updated for Plotly.js 3.0+
            layout_obj = {
                'title': {'text': title or '2D Linear Regression'},
                'xaxis': {
                    'title': {'text': x_label or 'X', 'font': {'size': 18}},
                    'showgrid': True,
                    'showline': True,
                    'tickfont': {'size': 14}
                },
                'yaxis': {
                    'title': {'text': y_label or 'y', 'font': {'size': 18}},
                    'showgrid': True,
                    'showline': True,
                    'tickfont': {'size': 14}
                },
                'height': custom_layout.get('height', 800),
                'width': custom_layout.get('width', 1000),
                'autosize': custom_layout.get('autosize', True),
                'margin': custom_layout.get('margin', {'l': 120, 'r': 80, 'b': 120, 't': 100, 'pad': 10})
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

            # Corrected layout for actual vs predicted - updated for Plotly.js 3.0+
            layout_obj = {
                'title': {'text': title or 'Actual vs Predicted'},
                'xaxis': {
                    'title': {'text': x_label or 'Actual y', 'font': {'size': 18}},
                    'showgrid': True,
                    'showline': True,
                    'tickfont': {'size': 14}
                },
                'yaxis': {
                    'title': {'text': y_label or 'Predicted y', 'font': {'size': 18}},
                    'showgrid': True,
                    'showline': True,
                    'tickfont': {'size': 14}
                },
                'height': custom_layout.get('height', 800),
                'width': custom_layout.get('width', 1000),
                'autosize': custom_layout.get('autosize', True),
                'margin': custom_layout.get('margin', {'l': 120, 'r': 80, 'b': 120, 't': 100, 'pad': 10})
            }

    # Convert the data to JSON
    plot_data_json = json.dumps(plot_data)
    layout_json = json.dumps(layout_obj)

    # Create a complete standalone HTML page with additional styling for better visibility
    html = f'''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Regression Analysis</title>
    <!-- Plotly JS -->
    <script src="https://cdn.plot.ly/plotly-3.0.1.min.js" charset="utf-8"></script>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f9f9f9;
        }}
        .container {{
            width: 95%;
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            padding: 20px;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
            border-radius: 5px;
        }}
        .plot-title {{
            text-align: center;
            margin-bottom: 20px;
            color: #333;
            font-size: 24px;
        }}
        .plot-container {{
            height: 700px;
            width: 100%;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1 class="plot-title">Linear Regression Analysis</h1>
        <div id="plot" class="plot-container"></div>
    </div>
    
    <script>
        window.onload = function() {{
            // Define the data
            const data = {plot_data_json};
            
            // Define the layout with responsive settings
            let layout = {layout_json};
            
            // Ensure margins are sufficient for axis labels
            if (!layout.margin) {{
                layout.margin = {{l: 120, r: 80, b: 120, t: 100, pad: 10}};
            }}
            
            // Ensure automargin is enabled for axis titles
            if (layout.xaxis) {{
                layout.xaxis.automargin = true;
            }}
            if (layout.yaxis) {{
                layout.yaxis.automargin = true;
            }}
            
            // Create the plot with modebar always visible
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
        }};
    </script>
</body>
</html>
'''

    print(f"Generated HTML with length: {len(html)}")

    return jsonify({'html': html})


if __name__ == '__main__':
    # Check environment to determine server mode
    env = os.getenv('FLASK_ENV', 'development')

    if env == 'production':
        # In production, use gunicorn (this code won't actually run as gunicorn will be started separately)
        print("Running in production mode - use gunicorn")
    else:
        # In development, use Flask's built-in server
        print(f"Running in {env} mode - using Flask's built-in server")
        app.run(host='0.0.0.0', port=8000, debug=True)