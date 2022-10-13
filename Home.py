import streamlit as st
from annoy import AnnoyIndex
import glob
from PIL import Image
import pandas as pd
from sentence_transformers import SentenceTransformer
import json
import gdown

def download_files():
    ann_file = "./mss_embeddings/clip_80_02k.ann"
    ann_url = "https://drive.google.com/file/d/1zc9FN9MJi2ex1WSLKvsqv1FdUSISWori/view?usp=sharing"

    npy_file = "./mss_embeddings/embeddings_0_80080.npy"
    npy_url = "https://drive.google.com/file/d/1lLxxJW_WJyn5LV4odW66pyzeTdDLGMqm/view?usp=sharing"

    index_file = "./mss_embeddings/index.csv"
    index_url = "https://drive.google.com/file/d/1Grdcidy3tvTaHIVf3Zll2VaOHranQEzS/view?usp=sharing"
    if os.path.exists(npy_file):
        pass
    else:
        gdown.download(npy_url, npy_file, quiet=False, fuzzy=True)


    if os.path.exists(ann_file):
        pass
    else:
        gdown.download(ann_url, ann_file, quiet=False, fuzzy=True)


    if os.path.exists(index_file):
        pass
    else:
        gdown.download(index_url, index_file, quiet=False, fuzzy=True)

        print("Download Complete")

# download_files()

@st.cache(allow_output_mutation=True)
def create_model():
    model = SentenceTransformer('clip-ViT-B-32')
    return model

def embed_image(img):
    # img = Image.open(filename)
    res = model.encode([img], show_progress_bar=False)[0]
    return res

def embed_text(text):
    res = model.encode([text], show_progress_bar=True)[0]
    return res

@st.cache
def load_image(image_file):
    img = Image.open(image_file)
    return img

@st.cache(allow_output_mutation=True)
def create_index():
    with open(f'mss_embeddings/embeddings_0_80080.json','r', encoding="utf-8") as embedding_file:
        embeddings_index = json.load(embedding_file)
    return embeddings_index


def get_similar_images_annoy(img_index, num, mode="item", v=0, text=""):
    if mode == "item":
        similar_img_ids = t.get_nns_by_item(img_index, num)
    elif mode == "vector":
        similar_img_ids = t.get_nns_by_vector(v, num)
    elif mode == "text":
        similar_img_ids = t.get_nns_by_vector(text, num)
    return similar_img_ids

@st.cache(allow_output_mutation=True)
def load_annoy_index():
    t = AnnoyIndex(512, metric="angular")
    t.load("mss_embeddings/clip_80_02k.ann")
    return t

@st.cache(allow_output_mutation=True)
def data_index():
    df = pd.read_csv("mss_embeddings/index.csv")
    df.index = df.id
    return df

def update_state():
    st.session_state["search_index"] = st.session_state["clicked"]
    st.session_state["search_mode"] = 0

model = create_model()
ecodices_index = data_index()
index = create_index()
t = load_annoy_index()

if "clicked" not in st.session_state:
    st.session_state["clicked"] = 0

if "search_index" not in st.session_state:
    st.session_state["search_index"] = 1

if "search_mode" not in st.session_state:
    st.session_state["search_mode"] = 0

mode = st.sidebar.selectbox("Mode", ["Index Search", "New Image Search", "Text Search"], index=st.session_state["search_mode"])
img = ""
if mode == "Index Search":
    img_index = st.sidebar.number_input("Index", value=st.session_state["search_index"])
elif mode == "New Image Search":
    image_file = st.sidebar.file_uploader("Uploade Image")
    if image_file is not None:
        file_details = {"FileName":image_file.name,"FileType":image_file.type}
        loaded_image = load_image(image_file)
        with open("tempDir/temp.jpg","wb") as f:
          f.write(image_file.getbuffer())
    # da = embed_image(f"tempDir/temp.jpg")
elif mode == "Text Search":
    query_text = st.sidebar.text_input("Query Text")
    if "medieval" not in query_text:
        query_text = "medieval "+query_text
    embedded_text = embed_text(query_text)

num_results = st.sidebar.number_input("Number of Results", 1, 100)
if mode =="Index Search":
    image_num = int(index[img_index])
    # st.write(image)
    search_image_df = ecodices_index.loc[ecodices_index.id == image_num]
    ignore_same_ms = st.sidebar.checkbox("Ignore Same Manuscript")
    # search_image_df = ecodices_index.loc[ecodices_index.id == img_index]
    si_shelfmark = search_image_df.shelfmark.tolist()[0]
    si_href = search_image_df.href.tolist()[0]
    si_label = search_image_df.label.tolist()[0]
    si_src = search_image_df.src.tolist()[0]
    res = get_similar_images_annoy(img_index, num_results+1)
    st.sidebar.markdown("## Search Image: ")
    st.sidebar.image(si_src.replace('full/,150', 'full/,500'))
    st.sidebar.markdown(f"[{si_shelfmark}, {si_label}]({si_href})", unsafe_allow_html=True)

    start = 1

elif mode == "New Image Search":
    start = 0
    img_embedding = embed_image(loaded_image)
    # st.write(img_embedding)
    res = get_similar_images_annoy(img_index=50, num=num_results, v=img_embedding, mode="vector")
    st.sidebar.markdown("## Search Image: ")
    if img_embedding != "":
        st.sidebar.image(loaded_image)

elif mode == "Text Search":
    start = 0
    # st.write(embedded_text)
    res = get_similar_images_annoy(img_index=50, num=num_results, mode="text", text = embedded_text)

st.markdown("## Results:")
current = 1
current_row = 1
cols = st.columns(4)
n=4


if mode == "Index Search":
    initial_l = res[start:]
    l = []
    for image in initial_l:
        image_num = int(index[image])
        # st.write(image)
        # search_image_df = ecodices_index.loc[ecodices_index.id == image_num]
        row = ecodices_index.loc[ecodices_index.id == image_num]
        shelfmark = row.shelfmark.tolist()[0]
        if ignore_same_ms:
            # st.write(shelfmark)
            # st.write(si_shelfmark)
            if shelfmark != si_shelfmark:
                l.append(image)
        else:
            l.append(image)
else:
    l = res[start:]

list_of_groups = [l[i:i+n] for i in range(0, len(l), n)]
buttons = []
button_index = []
for images in list_of_groups:
    captions = []
    for image in images:
        # st.write(image)
        # st.write(index[int(image)])
        image_num = int(index[image])
        # st.write(image)
        row = ecodices_index.loc[ecodices_index.id == image_num]
        shelfmark = row.shelfmark.tolist()[0]
        href = row.href.tolist()[0]
        label = row.label.tolist()[0]
        src = row.src.tolist()[0]
        captions.append((f"{shelfmark}, {label}.", f"{href}", f"{src}", image_num))
    # st.write(images)
    # st.write(index[1000])
    # images = [index[img] for img in images]
    cols = st.columns(4)
    for i in range(len(images)):
        cols[i].image(captions[i][2].replace('full/,150', 'full/,200'))
        cols[i].markdown(f"[{captions[i][0]}]({captions[i][1]})", unsafe_allow_html=True)
        buttons.append(cols[i].button(f"Index: {captions[i][3]}"))
        button_index.append(images[i])



for i, button in enumerate(buttons):
    if button:
        clicked = int(str(button_index[i]).replace("\\", "/").split("/")[-1].replace(".jpg", ""))
        st.session_state["search_index"] = clicked
        st.session_state["search_mode"] = 0













#
