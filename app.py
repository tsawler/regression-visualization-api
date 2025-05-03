from flask import Flask, request, jsonify
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
import io
import base64

# Initialize the Flask application
app = Flask(__name__)


def encode_image():
    """
    Helper function to encode matplotlib figure to base64.

    This converts the current matplotlib plot into a PNG image and encodes it as a base64 string,
    which can be embedded in HTML or returned in JSON responses.

    Returns:
        str: Base64 encoded string of the current matplotlib figure
    """
    buf = io.BytesIO()  # Create an in-memory binary stream
    # Save the current figure to the stream as PNG
    plt.savefig(buf, format='png')
    plt.close()  # Close the figure to free memory
    buf.seek(0)  # Rewind to the beginning of the stream
    # Encode binary data as base64 string
    return base64.b64encode(buf.read()).decode('utf-8')


@app.route('/regression', methods=['POST'])
def regression():
    """
    Endpoint to perform linear regression and generate visualizations.

    Accepts JSON data with X (features) and y (target) arrays, plot type, and custom labels.
    Fits a linear regression model and returns a visualization of the results.

    Expected JSON format:
    {
        "X": [[x1_1, x1_2, ...], [x2_1, x2_2, ...], ...],  # 2D array of features
        "y": [y1, y2, ...],  # 1D array of target values
        "plot": "2d" or "3d",  # Optional plot type parameter
        "labels": {  # Optional custom labels
            "title": "My Custom Plot Title",
            "x_label": "X Axis Label",
            "y_label": "Y Axis Label",
            "z_label": "Z Axis Label"  # Only used for 3D plots
        }
    }

    Returns:
        JSON response with base64 encoded image of the regression visualization
    """
    data = request.get_json()  # Parse the JSON request body
    X = np.array(data['X'])  # Convert X data to NumPy array
    y = np.array(data['y'])  # Convert y data to NumPy array
    plot_type = data.get('plot', '2d')  # Get plot type or default to '2d'

    # Get custom labels (if provided)
    labels = data.get('labels', {})
    title = labels.get('title', '')
    x_label = labels.get('x_label', '')
    y_label = labels.get('y_label', '')
    z_label = labels.get('z_label', '')

    # Create and train the linear regression model
    model = LinearRegression()
    model.fit(X, y)

    if plot_type == '3d':
        # Create a 3D visualization for exactly 2 features
        if X.shape[1] != 2:
            # Return error if X doesn't have exactly 2 columns for 3D plot
            return jsonify({'error': '3D plot requires exactly 2 features (columns) in X'}), 400

        fig = plt.figure()  # Create a new figure
        ax = fig.add_subplot(111, projection='3d')  # Add a 3D subplot
        ax.scatter(X[:, 0], X[:, 1], y, color='blue',
                   label='Actual')  # Plot actual data points

        # Create a mesh grid for the prediction surface
        x_surf, y_surf = np.meshgrid(
            # 20 points along X1 range
            np.linspace(X[:, 0].min(), X[:, 0].max(), 20),
            # 20 points along X2 range
            np.linspace(X[:, 1].min(), X[:, 1].max(), 20)
        )

        # Predict values for all points in the mesh grid and reshape to match grid dimensions
        z_surf = model.predict(
            np.c_[x_surf.ravel(), y_surf.ravel()]).reshape(x_surf.shape)

        # Plot the prediction surface
        ax.plot_surface(x_surf, y_surf, z_surf, alpha=0.5, color='red')

        # Set custom labels if provided
        if title:
            ax.set_title(title)
        ax.set_xlabel(x_label if x_label else "X1")
        ax.set_ylabel(y_label if y_label else "X2")
        ax.set_zlabel(z_label if z_label else "y")

        # Add a legend
        ax.legend()

    else:
        # Handle 2D plotting cases
        if X.shape[1] == 1:
            # Simple linear regression (one feature)
            # Plot actual data points
            plt.scatter(X, y, color='blue', label='Actual')
            plt.plot(X, model.predict(X), color='red',
                     label='Prediction')  # Plot prediction line

            # Set custom labels if provided
            if title:
                plt.title(title)
            plt.xlabel(x_label if x_label else "X")
            plt.ylabel(y_label if y_label else "y")

            # Add a legend
            plt.legend()

        else:
            # Multiple regression (more than one feature)
            # Plot predicted vs actual values to visualize model performance
            y_pred = model.predict(X)
            # Actual vs Predicted scatter plot
            plt.scatter(y, y_pred, color='green')
            plt.plot([y.min(), y.max()], [y.min(), y.max()],
                     'k--', lw=2)  # Perfect prediction line

            # Set custom labels if provided
            if title:
                plt.title(title if title else "Actual vs Predicted")
            plt.xlabel(x_label if x_label else "Actual y")
            plt.ylabel(y_label if y_label else "Predicted y")

    # Convert the plot to base64 encoded image
    image_base64 = encode_image()

    # Return the encoded image in the JSON response
    return jsonify({'image_base64': image_base64})


# Run the application if this file is executed directly
if __name__ == '__main__':
    # Start server on all network interfaces (0.0.0.0) on port 8000
    app.run(host='0.0.0.0', port=8000)
