# GrowMate

## AI-Powered Soil Analysis and Crop Recommendation

GrowMate is an AI-powered agriculture application that uses computer vision and environmental data to support soil analysis and crop selection.

The application analyzes an image of soil, classifies its texture using a machine learning model, and combines the result with environmental information to provide agricultural recommendations.

## Overview

GrowMate was developed to explore how machine learning can be applied to practical agricultural decision-making.

The core machine learning component uses transfer learning with MobileNetV2 to classify soil texture into three categories:

* Sandy
* Clay
* Loamy

The application also incorporates weather data to provide additional environmental context for its recommendations.

## Key Features

* Soil image classification using a MobileNetV2-based computer vision model
* Classification of soil into Sandy, Clay, and Loamy categories
* Crop recommendations based on soil characteristics
* Integration with weather data through an external API
* Soil and environmental analysis
* Interactive Streamlit interface
* Agricultural guidance and user challenges

## System Workflow

```text
User
  |
  v
Soil Image
  |
  v
Image Preprocessing
  |
  v
MobileNetV2 Model
  |
  v
Soil Texture Classification
  |
  v
Soil Analysis
  |
  +------------------+
  |                  |
  v                  v
Soil Information   Weather Data
  |                  |
  +--------+---------+
           |
           v
   Agricultural Analysis
           |
           v
   Crop Recommendations
```

## Machine Learning

The soil classification model uses transfer learning with MobileNetV2.

The model was trained using an augmented dataset containing 375 soil images across three soil texture classes:

| Class | Description                             |
| ----- | --------------------------------------- |
| Sandy | Soil with a predominantly sandy texture |
| Clay  | Soil with a predominantly clay texture  |
| Loamy | Soil with a predominantly loamy texture |

Transfer learning was selected to leverage a pretrained convolutional neural network while adapting the model to the soil classification task.

## Technology Stack

| Technology         | Purpose                                                 |
| ------------------ | ------------------------------------------------------- |
| Python             | Application and machine learning development            |
| TensorFlow / Keras | Model development and inference                         |
| MobileNetV2        | Transfer-learning architecture for image classification |
| Streamlit          | Interactive application interface                       |
| Pandas             | Data processing                                         |
| NumPy              | Numerical computation                                   |
| OpenWeatherMap API | Weather and environmental data                          |

## Project Structure
## Project Structure

```text
Growmate/
├── .streamlit/          # Streamlit configuration
├── app/                 # Application interface and application logic
├── data/                # Dataset and data assets
├── models/              # Trained machine learning models
├── results/             # Model outputs and evaluation results
├── dataset_figures.py   # Dataset visualization utilities
├── evaluate_model.py    # Model evaluation
├── prepare_data.py      # Data preprocessing and preparation
├── train_model.py       # Model training
├── run.py               # Application entry point
├── requirements.txt     # Python dependencies
├── .gitignore
├── LICENSE
└── README.md
```

## Installation

### Clone the repository

```bash
git clone https://github.com/uzochichinedu79-alt/Growmate.git
cd Growmate
```

### Create a virtual environment

```bash
python -m venv .venv
```

On Windows:

```bash
.venv\Scripts\activate
```

On macOS/Linux:

```bash
source .venv/bin/activate
```

### Install dependencies

```bash
pip install -r requirements.txt
```

### Configure environment variables

If the application requires an API key, create a `.env` file or configure the required environment variables according to the application's configuration.

Do not commit API keys or other secrets to the repository.

### Run the application

```bash
streamlit run app.py
```

## Project Objectives

GrowMate explores the use of machine learning and environmental data to support more accessible agricultural decision-making.

The project focuses on:

1. Applying computer vision to soil classification.
2. Using transfer learning for a practical image classification problem.
3. Combining machine learning outputs with external environmental data.
4. Building an accessible interface for interacting with an ML application.

## Future Improvements

Potential areas for further development include:

* Expanding the soil image dataset
* Increasing the number of soil classes
* Improving model performance with additional training data
* Adding more agricultural and soil features
* Expanding crop coverage
* Improving crop recommendation logic
* Adding automated model evaluation and monitoring
* Deploying the application for broader use

## Author

**Uzochi Chinedu**

AI Engineer | Computer Science

[GitHub](https://github.com/uzochichinedu79-alt)
