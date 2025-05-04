# Regression Analysis API

A Flask-based API service for performing linear regression analysis with interactive Plotly visualizations.

## Overview

This project provides a simple HTTP API that performs linear regression on provided data points and returns a complete interactive HTML visualization using Plotly. The API supports both 2D and 3D regression visualizations, making it useful for data analysis and machine learning projects.

## Features

- **2D Linear Regression** - For single feature datasets
- **Multi-feature Regression** - Visualizes actual vs. predicted values
- **3D Surface Plots** - For datasets with exactly 2 features
- **Customizable Plots** - Control titles, labels, dimensions, and layout
- **Interactive Visualizations** - Fully interactive Plotly graphs with zoom, pan and rotation capabilities
- **Responsive Design** - Plots resize to fit the viewing window
- **Docker Support** - Easy deployment using Docker and Docker Compose

## Installation

### Prerequisites

- Python 3.8 or higher
- Docker and Docker Compose (optional for containerized deployment)

### Method 1: Direct Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/regression-analysis-api.git
   cd regression-analysis-api
   ```

2. Create and activate a virtual environment (optional but recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the application:
   ```bash
   python app.py
   ```

The API will be available at `http://localhost:8000`.

### Method 2: Docker Deployment

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/regression-analysis-api.git
   cd regression-analysis-api
   ```

2. Build and start the Docker container:
   ```bash
   docker-compose up -d
   ```

The API will be available at `http://localhost:8000`.

## API Usage

The API exposes a single endpoint at the root path (`/`) that accepts POST requests with JSON data.

### Request Format

```json
{
  "X": [[x1], [x2], ...],
  "y": [y1, y2, ...],
  "plot": "2d",
  "labels": {
    "title": "My Regression Analysis",
    "x_label": "Feature 1",
    "y_label": "Target",
    "z_label": "Z Axis"
  },
  "layout": {
    "height": 800,
    "width": 1000,
    "autosize": true,
    "margin": {"l": 80, "r": 80, "b": 80, "t": 100, "pad": 4}
  }
}
```

### Parameters

- `X` (required): 2D array of feature values. For 2D plots, use a single column. For 3D plots, use exactly 2 columns.
- `y` (required): Array of target values.
- `plot` (optional): Plot type, either "2d" (default) or "3d".
- `labels` (optional): Object containing custom labels:
  - `title`: Plot title
  - `x_label`: X-axis label
  - `y_label`: Y-axis label
  - `z_label`: Z-axis label (for 3D plots)
- `layout` (optional): Custom layout options for the Plotly plot:
  - `height`: Plot height in pixels
  - `width`: Plot width in pixels
  - `autosize`: Whether to allow plot resizing
  - `margin`: Margins around the plot

### Response

The API returns a JSON object with a single field `html` containing the complete HTML page with the interactive Plotly visualization.

```json
{
  "html": "<!DOCTYPE html>..."
}
```

## Example: Go Client

Here's a sample Go program that demonstrates how to request both 2D and 3D visualizations from the API:

```go
package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io/ioutil"
	"net/http"
	"os"
)

type RegressionRequest struct {
	X      [][]float64          `json:"X"`
	Y      []float64            `json:"y"`
	Plot   string               `json:"plot,omitempty"`
	Labels map[string]string    `json:"labels,omitempty"`
	Layout map[string]interface{} `json:"layout,omitempty"`
}

type RegressionResponse struct {
	HTML string `json:"html"`
}

func main() {
	baseURL := "http://localhost:8000"

	// Example 1: 2D Regression
	fmt.Println("Generating 2D Regression Plot...")
	
	request2D := RegressionRequest{
		X: [][]float64{
			{1.0}, {2.0}, {3.0}, {4.0}, {5.0}, {6.0}, {7.0}, {8.0}, {9.0}, {10.0},
		},
		Y: []float64{2.0, 4.1, 6.3, 8.0, 9.8, 11.9, 14.1, 16.0, 18.2, 20.1},
		Plot: "2d",
		Labels: map[string]string{
			"title":   "Linear Relationship Example",
			"x_label": "Input Feature",
			"y_label": "Target Value",
		},
	}
	
	html2D := makeRegressionRequest(baseURL, request2D)
	err := saveHTML("regression_2d.html", html2D)
	if err != nil {
		fmt.Printf("Error saving 2D HTML: %v\n", err)
	} else {
		fmt.Println("2D regression plot saved to regression_2d.html")
	}

	// Example 2: 3D Regression
	fmt.Println("\nGenerating 3D Regression Plot...")
	
	// Create some sample 3D data with two features
	var x3D [][]float64
	var y3D []float64
	
	// Generate synthetic data where z ≈ 2x + 3y + random noise
	for x := 0.0; x <= 10.0; x += 1.0 {
		for y := 0.0; y <= 10.0; y += 1.0 {
			// Add some random noise to make it interesting
			noise := -0.5 + rand.Float64() // Random value between -0.5 and 0.5
			z := 2*x + 3*y + noise
			
			x3D = append(x3D, []float64{x, y})
			y3D = append(y3D, z)
		}
	}
	
	request3D := RegressionRequest{
		X:    x3D,
		Y:    y3D,
		Plot: "3d",
		Labels: map[string]string{
			"title":   "Multi-feature Regression Surface",
			"x_label": "Feature 1",
			"y_label": "Feature 2",
			"z_label": "Target Value",
		},
		Layout: map[string]interface{}{
			"height": 800,
			"width": 1000,
		},
	}
	
	html3D := makeRegressionRequest(baseURL, request3D)
	err = saveHTML("regression_3d.html", html3D)
	if err != nil {
		fmt.Printf("Error saving 3D HTML: %v\n", err)
	} else {
		fmt.Println("3D regression plot saved to regression_3d.html")
	}
}

func makeRegressionRequest(baseURL string, request RegressionRequest) string {
	reqBody, err := json.Marshal(request)
	if err != nil {
		fmt.Printf("Error marshaling request: %v\n", err)
		return ""
	}

	resp, err := http.Post(baseURL+"/", "application/json", bytes.NewBuffer(reqBody))
	if err != nil {
		fmt.Printf("Error making request: %v\n", err)
		return ""
	}
	defer resp.Body.Close()

	body, err := ioutil.ReadAll(resp.Body)
	if err != nil {
		fmt.Printf("Error reading response: %v\n", err)
		return ""
	}

	if resp.StatusCode != http.StatusOK {
		fmt.Printf("Error response (Status %d): %s\n", resp.StatusCode, string(body))
		return ""
	}

	var response RegressionResponse
	err = json.Unmarshal(body, &response)
	if err != nil {
		fmt.Printf("Error unmarshaling response: %v\n", err)
		return ""
	}

	return response.HTML
}

func saveHTML(filename string, html string) error {
	return ioutil.WriteFile(filename, []byte(html), 0644)
}
```

Note: You'll need to import the `math/rand` package and add `rand.Seed(time.Now().UnixNano())` in your main function for the 3D example to work properly.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.

## Credits

Developed by Trevor Sawler © 2025

Built with:
- [Flask](https://flask.palletsprojects.com/) - Web framework
- [NumPy](https://numpy.org/) - Numerical computing
- [scikit-learn](https://scikit-learn.org/) - Machine learning tools
- [Plotly](https://plotly.com/) - Interactive visualizations

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.