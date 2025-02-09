import fitz
import os
from pathlib import Path
import json


def run_docker(input_dir, output_dir):
    pdf_name = os.listdir(input_dir)[0]
    print(pdf_name)
    os.system(f"sudo docker run --rm --volume {output_dir}:/work/host-output --volume {input_dir}:/work/host-input dzeri96/deepfigures-cpu:0.0.3 python3 /work/scripts/rundetection.py /work/host-output /work/host-input/{pdf_name}")

    docker_output = os.listdir(output_dir)[0]
    print(docker_output)
    if len(docker_output) > 0:
        json_path = os.path.join(output_dir ,docker_output, 'pdffigures', f"{pdf_name[:-4]}.json")
    else:
        raise ValueError(f"No output found in {output_dir}")

    with open(json_path) as f:
        data = json.load(f)

    region_boundary = data['figures'][0]['regionBoundary']
    os.system(f"sudo rm -rf {os.path.join(output_dir, docker_output)}")
    print(f"Deleted the folder: {docker_output}")


    return region_boundary


def extract_figure(input_pdf, output_image, region_boundary, dpi=300):
    try:
        Path(output_image).parent.mkdir(parents=True, exist_ok=True)

        with fitz.open(input_pdf) as doc:
            page = doc[0]  # Assuming extracting from the first page

            # Extract the figure region using the region_boundary
            rect = fitz.Rect(
                region_boundary['x1'],
                region_boundary['y1'],
                region_boundary['x2'],
                region_boundary['y2']
            )
            
            # Generate the image from the specified region
            pix = page.get_pixmap(
                clip=rect, 
                dpi=dpi, 
                colorspace="rgb"
            )

            # Save the extracted image
            pix.save(output_image)
            print(f"Successfully saved image to {output_image}")

    except Exception as e:
        print(f"Error extracting figure from {input_pdf}: {str(e)}")


if __name__ == "__main__":

    input_pdf_dir = Path("/home/nikant/Desktop/texttodia/input")
    sample_pdf = input_pdf_dir / "test2.pdf"
    # Run Docker to detect figures and get the region boundary
    region_boundary = run_docker(input_pdf_dir, "/home/nikant/Desktop/texttodia/output")

    # Configuration for figure extraction, using region_boundary from Docker output
    config = {
        "input_pdf": str(sample_pdf),
        "output_image": "/home/nikant/Desktop/texttodia/test1.png",
        "region_boundary": region_boundary,  # Use region_boundary from Docker
        "dpi": 300
    }

    # Extract the figure from the PDF based on the region boundary
    extract_figure(**config)
