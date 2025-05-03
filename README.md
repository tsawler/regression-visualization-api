# Regression Visualization API

A simple yet powerful Flask API for performing linear regression analysis and generating interactive visualizations using Plotly.

## Features

- Perform linear regression on your data
- Generate interactive 2D visualizations for single-feature regression
- Generate interactive 3D visualizations for two-feature regression
- Output embeddable HTML for web applications
- Containerized for easy deployment

## Installation

### Prerequisites

- Docker and Docker Compose
- Git (for cloning the repository)

### Option 1: Using Docker Compose (Recommended)

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/regression-api.git
   cd regression-api
   ```

2. Start the container:
   ```bash
   docker-compose up -d
   ```

The API will be accessible at `http://localhost:8000`.

### Option 2: Manual Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/regression-api.git
   cd regression-api
   ```

2. Create a virtual environment:
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

The API will be accessible at `http://localhost:8000`.

## API Endpoints

### `/regression` [POST]

Performs linear regression on input data and returns interactive Plotly visualizations.

**Request Format:**

```json
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
```

> **Note**: The API returns a standard Plotly HTML element with default sizing. To increase the size of the visualization (especially recommended for 3D plots), you can modify the returned HTML by replacing the style attribute as shown in the examples below.

**Response Format:**

```json
{
    "html": "<!-- Interactive Plotly HTML -->"
}
```

## Usage Examples

> **Note**: The default plot size may appear small, especially for 3D visualizations. All examples below include code to increase the size of the plots for better viewing.

### Example 1: Simple 2D Regression with CURL

```bash
curl -X POST http://localhost:8000/regression \
  -H "Content-Type: application/json" \
  -d '{
    "X": [[1], [2], [3], [4], [5]],
    "y": [2, 3.9, 6.1, 8, 9.8],
    "plot": "2d",
    "labels": {
      "title": "Simple Linear Regression",
      "x_label": "Input Feature",
      "y_label": "Target Value"
    }
  }'
```

### Example 2: 3D Regression with CURL

```bash
curl -X POST http://localhost:8000/regression \
  -H "Content-Type: application/json" \
  -d '{
    "X": [[1, 2], [2, 3], [3, 5], [4, 2], [5, 1]],
    "y": [3, 6, 14, 8, 9],
    "plot": "3d",
    "labels": {
      "title": "Multiple Linear Regression",
      "x_label": "Feature 1",
      "y_label": "Feature 2",
      "z_label": "Target Value"
    }
  }'
```

### Example 3: Python Client

```python
import requests
import json
import numpy as np
from IPython.display import HTML

# Sample data
X = np.array([[1, 2], [2, 1], [3, 3], [4, 2], [5, 4]])
y = np.array([3, 4, 7, 7, 10])

# Prepare request payload
payload = {
    "X": X.tolist(),
    "y": y.tolist(),
    "plot": "3d",
    "labels": {
        "title": "Housing Price Prediction",
        "x_label": "Size (sq ft)",
        "y_label": "Age (years)",
        "z_label": "Price ($)"
    }
}

# Send request
response = requests.post(
    "http://localhost:8000/regression", 
    json=payload
)

# For a larger plot, you can modify the height and width
html_content = response.json()["html"]
# Increase the size - adjust the width and height as needed
larger_html = html_content.replace('style="height: 100%; width: 100%;"', 
                                  'style="height: 800px; width: 100%;"')

# Display the visualization (in Jupyter Notebook)
HTML(larger_html)

# Or save to file
with open("visualization.html", "w") as f:
    f.write(larger_html)
```

### Example 4: JavaScript Client

```javascript
async function fetchRegression() {
    const data = {
        "X": [[1], [2], [3], [4], [5]],
        "y": [2, 4.1, 5.9, 8.2, 9.9],
        "plot": "2d",
        "labels": {
            "title": "Sales Prediction",
            "x_label": "Marketing Budget ($K)",
            "y_label": "Sales ($K)"
        }
    };

    try {
        const response = await fetch('http://localhost:8000/regression', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });
        
        const result = await response.json();
        
        // Resize the plot by modifying the HTML
        const resizedHtml = result.html.replace(
            'style="height: 100%; width: 100%;"', 
            'style="height: 600px; width: 100%;"'
        );
        
        // Insert the visualization into a div
        document.getElementById('visualization').innerHTML = resizedHtml;
    } catch (error) {
        console.error('Error:', error);
    }
}

// Call the function when needed
fetchRegression();
```

### Example 5: Go Client

```go
package main

import (
    "bytes"
    "encoding/json"
    "fmt"
    "io/ioutil"
    "net/http"
    "os"
    "strings"
)

type RegressionRequest struct {
    X      [][]float64        `json:"X"`
    Y      []float64          `json:"y"`
    Plot   string             `json:"plot"`
    Labels map[string]string  `json:"labels"`
}

type RegressionResponse struct {
    HTML string `json:"html"`
}

func main() {
    // Sample data
    data := RegressionRequest{
        X:    [][]float64{{1}, {2}, {3}, {4}, {5}},
        Y:    []float64{2, 4, 6, 8, 10},
        Plot: "2d",
        Labels: map[string]string{
            "title":   "Go Client Example",
            "x_label": "Input",
            "y_label": "Output",
        },
    }

    jsonData, err := json.Marshal(data)
    if err != nil {
        fmt.Println("Error marshalling JSON:", err)
        return
    }

    resp, err := http.Post(
        "http://localhost:8000/regression",
        "application/json",
        bytes.NewBuffer(jsonData),
    )
    if err != nil {
        fmt.Println("Error sending request:", err)
        return
    }
    defer resp.Body.Close()

    body, err := ioutil.ReadAll(resp.Body)
    if err != nil {
        fmt.Println("Error reading response:", err)
        return
    }

    var result RegressionResponse
    if err := json.Unmarshal(body, &result); err != nil {
        fmt.Println("Error unmarshalling response:", err)
        return
    }

    // Resize the plot for better visualization
    resizedHTML := strings.Replace(
        result.HTML,
        `style="height: 100%; width: 100%;"`,
        `style="height: 700px; width: 100%;"`,
        1,
    )

    // Save the visualization to a file
    if err := ioutil.WriteFile("visualization.html", []byte(resizedHTML), 0644); err != nil {
        fmt.Println("Error writing HTML to file:", err)
        return
    }

    fmt.Println("Visualization saved to visualization.html")
}
```

## Requirements

The following dependencies are required and will be installed automatically when using Docker or the requirements.txt file:

- Flask
- NumPy
- scikit-learn
- Plotly

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.