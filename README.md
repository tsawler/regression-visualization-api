# Regression Visualization API

A Flask-based microservice that generates regression visualizations from data. This service is designed to run as a Docker sidecar container and provides regression analysis with both 2D and 3D visualization capabilities.

## Features

- Simple HTTP API for regression analysis
- Generates linear regression models using scikit-learn
- Supports both 2D and 3D visualizations
- Customizable plot titles and axis labels
- Returns base64-encoded PNG images
- Dockerized for easy deployment and integration

## Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/regression` | POST | Performs linear regression on provided data and returns a visualization as a base64-encoded PNG image |

## Installation

### Prerequisites

- Docker
- Docker Compose

### Setup

1. Clone this repository:
   ```bash
   git clone <your-repository-url>
   cd <repository-directory>
   ```

2. Build and start the Docker container:
   ```bash
   docker-compose up -d
   ```

The service will be available at `http://localhost:8000`.

## API Reference

### POST /regression

Performs linear regression on provided data and returns a visualization.

#### Request Body

JSON object with the following fields:

- `X` (required): 2D array for multi-feature regression or 1D array for simple regression
- `y` (required): 1D array of target values
- `plot` (optional): String specifying plot type - either `"2d"` (default) or `"3d"`
- `labels` (optional): Object containing custom labels for the plot:
  - `title` (optional): Custom title for the plot
  - `x_label` (optional): Custom label for the X-axis
  - `y_label` (optional): Custom label for the Y-axis
  - `z_label` (optional): Custom label for the Z-axis (only used in 3D plots)

#### Sample Request (Simple Linear Regression with Custom Labels)

```json
{
  "X": [[1], [2], [3], [4], [5]],
  "y": [2, 4, 5, 4, 6],
  "plot": "2d",
  "labels": {
    "title": "Sales vs. Advertising",
    "x_label": "Advertising Budget ($1000s)",
    "y_label": "Sales Revenue ($10,000s)"
  }
}
```

#### Sample Request (Multiple Linear Regression with 3D Plot and Custom Labels)

```json
{
  "X": [[1, 1], [2, 2], [3, 3], [4, 5], [5, 4]],
  "y": [2, 4, 5, 7, 6],
  "plot": "3d",
  "labels": {
    "title": "Product Sales Model",
    "x_label": "Price",
    "y_label": "Marketing",
    "z_label": "Units Sold"
  }
}
```

#### Response

JSON object with:
- `image_base64`: Base64-encoded PNG image of the regression visualization

#### Sample Response

```json
{
  "image_base64": "iVBORw0KGgoAAAANSUhEUgAA...AASUVORK5CYII="
}
```

#### Error Response

```json
{
  "error": "3D plot requires exactly 2 features (columns) in X"
}
```

#### HTTP Status Codes

- `200 OK`: Request successful
- `400 Bad Request`: When input data is invalid or incompatible with the requested plot type

## Usage Examples

### Simple Linear Regression (2D) with Custom Labels

```bash
curl -X POST http://localhost:8000/regression \
  -H "Content-Type: application/json" \
  -d '{
    "X": [[1], [2], [3], [4], [5]],
    "y": [2, 4, 5, 4, 6],
    "plot": "2d",
    "labels": {
      "title": "Sales vs. Advertising",
      "x_label": "Advertising Budget ($1000s)",
      "y_label": "Sales Revenue ($10,000s)"
    }
  }'
```

### Multiple Linear Regression with 2D Visualization

```bash
curl -X POST http://localhost:8000/regression \
  -H "Content-Type: application/json" \
  -d '{
    "X": [[1, 1], [2, 2], [3, 3], [4, 5], [5, 4]],
    "y": [2, 4, 5, 7, 6],
    "labels": {
      "title": "Performance Analysis",
      "x_label": "Actual Performance",
      "y_label": "Predicted Performance"
    }
  }'
```

This will produce an "Performance Analysis" plot with custom axis labels since we have multiple features.

### Multiple Linear Regression with 3D Visualization and Custom Labels

```bash
curl -X POST http://localhost:8000/regression \
  -H "Content-Type: application/json" \
  -d '{
    "X": [[1, 1], [2, 2], [3, 3], [4, 5], [5, 4]],
    "y": [2, 4, 5, 7, 6],
    "plot": "3d",
    "labels": {
      "title": "Product Sales Model",
      "x_label": "Price",
      "y_label": "Marketing",
      "z_label": "Units Sold"
    }
  }'
```

## Working with the API Response

The API returns a base64-encoded PNG image. To display or save this image:

### Python Example

```python
import requests
import base64
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import io

response = requests.post(
    "http://localhost:8000/regression",
    json={
        "X": [[1], [2], [3], [4], [5]],
        "y": [2, 4, 5, 4, 6],
        "labels": {
            "title": "Monthly Sales Trend",
            "x_label": "Month",
            "y_label": "Sales ($1000s)"
        }
    }
)

img_data = base64.b64decode(response.json()['image_base64'])
img = mpimg.imread(io.BytesIO(img_data))
plt.imshow(img)
plt.axis('off')
plt.show()
```

### JavaScript Example

```javascript
fetch('http://localhost:8000/regression', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    X: [[1], [2], [3], [4], [5]],
    y: [2, 4, 5, 4, 6],
    labels: {
      title: 'Website Traffic Analysis',
      x_label: 'Marketing Spend ($1000s)',
      y_label: 'Visitors (1000s)'
    }
  }),
})
.then(response => response.json())
.then(data => {
  const img = document.createElement('img');
  img.src = `data:image/png;base64,${data.image_base64}`;
  document.body.appendChild(img);
})
.catch(error => console.error('Error:', error));
```

### Go Example

```go
package main

import (
	"bytes"
	"encoding/base64"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"os"
)

// Labels structure for custom plot labels
type Labels struct {
	Title   string `json:"title,omitempty"`
	XLabel  string `json:"x_label,omitempty"`
	YLabel  string `json:"y_label,omitempty"`
	ZLabel  string `json:"z_label,omitempty"`
}

// Request structure that matches the API's expected format
type RegressionRequest struct {
	X      [][]float64 `json:"X"`
	Y      []float64   `json:"y"`
	Plot   string      `json:"plot,omitempty"`
	Labels *Labels     `json:"labels,omitempty"`
}

// Response structure for the API's return format
type RegressionResponse struct {
	ImageBase64 string `json:"image_base64"`
	Error       string `json:"error,omitempty"`
}

func main() {
	// Create the request payload with custom labels
	requestData := RegressionRequest{
		X: [][]float64{
			{1}, {2}, {3}, {4}, {5},
		},
		Y:    []float64{2, 4, 5, 4, 6},
		Plot: "2d",
		Labels: &Labels{
			Title:  "Quarterly Revenue Growth",
			XLabel: "Quarter",
			YLabel: "Revenue Growth (%)",
		},
	}

	// Marshal the request data to JSON
	jsonData, err := json.Marshal(requestData)
	if err != nil {
		fmt.Printf("Error marshaling JSON: %v\n", err)
		return
	}

	// Create the HTTP request
	req, err := http.NewRequest("POST", "http://localhost:8000/regression", bytes.NewBuffer(jsonData))
	if err != nil {
		fmt.Printf("Error creating request: %v\n", err)
		return
	}
	req.Header.Set("Content-Type", "application/json")

	// Send the request
	client := &http.Client{}
	resp, err := client.Do(req)
	if err != nil {
		fmt.Printf("Error sending request: %v\n", err)
		return
	}
	defer resp.Body.Close()

	// Read and parse the response
	body, err := io.ReadAll(resp.Body)
	if err != nil {
		fmt.Printf("Error reading response: %v\n", err)
		return
	}

	var response RegressionResponse
	err = json.Unmarshal(body, &response)
	if err != nil {
		fmt.Printf("Error unmarshaling response: %v\n", err)
		return
	}

	// Check for API error
	if response.Error != "" {
		fmt.Printf("API returned an error: %s\n", response.Error)
		return
	}

	// Decode the base64 image
	imgData, err := base64.StdEncoding.DecodeString(response.ImageBase64)
	if err != nil {
		fmt.Printf("Error decoding base64: %v\n", err)
		return
	}

	// Save the image to a file
	err = os.WriteFile("regression_plot.png", imgData, 0644)
	if err != nil {
		fmt.Printf("Error saving image: %v\n", err)
		return
	}

	fmt.Println("Regression plot saved as regression_plot.png")
}
```

## Technical Details

The service uses:
- Flask 3.0.2 for the HTTP API
- NumPy 2.2.5 for numerical operations
- Matplotlib 3.10.1 for visualization
- scikit-learn 1.6.1 for regression models

The Docker container exposes port 8000.

## Limitations

- 3D plots require exactly 2 features (columns) in X
- No persistent storage of models or results
- Limited to linear regression models

## Troubleshooting

### Common Issues

1. **Port conflicts**: If port 8000 is already in use, modify the `docker-compose.yml` file to use a different port mapping.

2. **Memory issues**: For large datasets, you might need to allocate more memory to Docker.

3. **Image not rendering**: Ensure your client application correctly handles base64-encoded PNG data.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.