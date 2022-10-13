# About this Project

This application is in alpha testing. It is an index of 80,080 manuscript images. These were gathered via the IIIF manifests for manuscripts on [E-Codices](https://www.e-codices.unifr.ch/), an invaluable database of manuscripts.

# How to Use the Application

Users can perform three types of searches.

1) Index Search - Use the E-Codices index for a given manuscript page. This can be difficult to find as this data is not easily discoverable unless one can parse the IIIF Manifest
2) New Image Search - Use an existing image to use as the basis for your query. In this case, the image will be embedded and then its similarity will be examined against all known images.
3) Text Search - Here, we can leverage CLIP embeddings which are pre-trained on images and captions. This means the model can find results in images based purely on text-based query. Because CLIP models are not trained explicitly on medieval images, I have added the word "medieval" to each search.

# Methodology

The methodology for this application was as follows:

1) Embed all images with `clip-ViT-B-32` using the [Sentence Transformer](https://github.com/UKPLab/sentence-transformers) library.
2) Create an Annoy Index of those embeddings to map similarity. Once found, results from the index are populated with links to E-Codices.
3) Streamlit to develop the front-end

All aspects of this app were done via Python.
