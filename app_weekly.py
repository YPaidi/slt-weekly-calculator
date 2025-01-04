from flask import Flask, render_template, request, jsonify
import matplotlib.pyplot as plt
import numpy as np
import io
import base64

app = Flask("SLT_Weekly_App")

# Function to calculate SLT and generate a correctly scaled graph
def calculate_slt(slt_type, synchronous_lecture, synchronous_activities, synchronous_assessment,
                  asynchronous_lecture, asynchronous_activities, asynchronous_assessment,
                  synchronous_lecture_prep, synchronous_activities_prep, synchronous_assessment_prep,
                  asynchronous_lecture_prep, asynchronous_activities_prep, asynchronous_assessment_prep):

    total_synchronous = (synchronous_lecture + synchronous_activities + synchronous_assessment +
                          synchronous_lecture_prep + synchronous_activities_prep + synchronous_assessment_prep)

    total_asynchronous = (asynchronous_lecture + asynchronous_activities + asynchronous_assessment +
                           asynchronous_lecture_prep + asynchronous_activities_prep + asynchronous_assessment_prep)

    total_slt = total_synchronous + total_asynchronous

    # Set SLT version constraints dynamically
    slt_versions = {
        "80": {"max_slt": 80, "min_async": 24, "max_async": 48},
        "120": {"max_slt": 120, "min_async": 36, "max_async": 72},
        "160": {"max_slt": 160, "min_async": 48, "max_async": 96}
    }

    if slt_type not in slt_versions:
        return None, "Invalid SLT type!", ""

    max_slt = slt_versions[slt_type]["max_slt"]
    min_async = slt_versions[slt_type]["min_async"]
    max_async = slt_versions[slt_type]["max_async"]

    # Check if total SLT matches the selected SLT version
    if total_slt != max_slt:
        warning = f"Warning: Total SLT should be exactly {max_slt} hours."
    else:
        warning = ""

    # Set bar color: Green if async is between min and max, otherwise red
    bar_color = 'green' if min_async <= total_asynchronous <= max_async else 'red'

    # Generate the plot with dynamic y-axis
    fig, ax = plt.subplots()
    ax.bar(['Asynchronous Learning Hours'], [total_asynchronous], color=bar_color)
    ax.axhline(y=min_async, color='black', linestyle='--', label=f'Minimum {min_async} Hours (30%)')
    ax.axhline(y=max_async, color='black', linestyle='--', label=f'Maximum {max_async} Hours (60%)')
    ax.set_ylim(0, max_slt)  # Dynamically set the y-axis max based on SLT version
    ax.set_ylabel("Hours of Asynchronous Learning")
    ax.set_title(f"Student Learning Time Distribution ({max_slt} Hours)")
    ax.legend()

    # Convert plot to image
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    graph_url = base64.b64encode(img.getvalue()).decode()
    plt.close(fig)

    return total_asynchronous, warning, graph_url

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        data = request.form
        slt_type = data['slt_type']  # Get SLT type (80, 120, or 160)

        total_asynchronous, warning, graph_url = calculate_slt(
            slt_type,
            int(data['synchronous_lecture']), int(data['synchronous_activities']), int(data['synchronous_assessment']),
            int(data['asynchronous_lecture']), int(data['asynchronous_activities']), int(data['asynchronous_assessment']),
            int(data['synchronous_lecture_prep']), int(data['synchronous_activities_prep']), int(data['synchronous_assessment_prep']),
            int(data['asynchronous_lecture_prep']), int(data['asynchronous_activities_prep']), int(data['asynchronous_assessment_prep'])
        )
        return jsonify({'total_asynchronous': total_asynchronous, 'warning': warning, 'graph_url': graph_url})

    return render_template('index.html', developer_name="Developed by [Rohayati Paidi]")

if __name__ == '__main__':
    app.run(debug=True, port=5050)  # Different port

