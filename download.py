import requests
import os
import json

def get_session_token(api_key):
    url = "https://tile.googleapis.com/v1/createSession?key={}".format(api_key)
    headers = {'Content-Type': 'application/json'}
    data = {
        "mapType": "streetview",
        "language": "en-US",
        "region": "US"
    }
    response = requests.post(url, headers=headers, data=json.dumps(data))
    if response.status_code == 200:
        session_token = response.json().get('session')
        print("Session token obtained:", session_token)
        return session_token
    else:
        print("Failed to obtain session token:", response.text)
        return None

def get_street_view_images(lat, lng, radius, api_key, world_coordinate=256, zoom_level=2, lat_range=1, lng_range=1, coord_prec=0.01):
    session_token = get_session_token(api_key)
    if not session_token:
        return

    pano_ids_url = f"https://tile.googleapis.com/v1/streetview/panoIds?session={session_token}&key={api_key}"
    locations = []
    img_prefix = []
    for lat_idx in range(-lat_range, lat_range+1):
        for lng_idx in range(-lng_range, lng_range+1):
            locations.append({"lat": lat + coord_prec * lat_idx, "lng": lng + coord_prec * lng_idx})
            img_prefix.append(f"lat{lat_idx}_lng{lng_idx}")
    payload = {
        "locations": locations,
        "radius": radius,
        "source": "outdoor"
    }
    headers = {'Content-Type': 'application/json'}
    response = requests.post(pano_ids_url, json=payload, headers=headers)
    pano_ids = response.json().get('panoIds', [])
    print("Summary", len(pano_ids), "panos")
    print(pano_ids)
    meta_data_dict = {}

    for counter, pano_id in enumerate(pano_ids):
        if pano_id:
            # Get metadata
            metadata_url = f"https://tile.googleapis.com/v1/streetview/metadata?session={session_token}&key={api_key}&panoId={pano_id}"
            prefix = img_prefix[counter]
            response = requests.get(metadata_url)
            metadata = response.json()
            meta_data_dict[prefix] = metadata
            tile_height = metadata["tileHeight"]
            tile_width = metadata["tileWidth"]
            image_height = metadata["imageHeight"]
            image_width = metadata["imageWidth"]
            print(round(metadata["lat"] - lat, 4), round(metadata["lng"] - lng, 4))
            x_range = max((image_width // tile_width) // (2 ** (5 - zoom_level)), 1)
            y_range = max((image_height // tile_height) // (2 ** (5 - zoom_level)), 1)
            print("Total", x_range * y_range, "images.")
            for x in range(x_range):
                for y in range(y_range):
                    image_url = f"https://tile.googleapis.com/v1/streetview/tiles/{zoom_level}/{x}/{y}?session={session_token}&key={api_key}&panoId={pano_id}"
                    image_response = requests.get(image_url)
                    if image_response.status_code == 200:
                        file_path = os.path.join("street_view_images", f"{prefix}_{x}_{y}.jpg")
                        with open(file_path, 'wb') as file:
                            file.write(image_response.content)
                        print(f"Image saved: {file_path}")
                    else:
                        import pdb; pdb.set_trace()
                        print(f"Failed to download image for panoId: {pano_id}")
        else:
            print("Invalid panoId found.")
    with open(os.path.join("street_view_images", "metadata.json"), "w") as f:
        json.dump(meta_data_dict, f)

if __name__ == "__main__":
    api_key = open("api_key.txt").readline().strip()
    # try to request (2*lat_range+1)*(2*lng_range+1) street view images at position with grid size of coord_prec
    # -1,1  0,1  1,1
    # -1,0  0,0  1,0
    # -1,-1 0,-1 1,-1
    # zoom level 0-5 (5 will have many many images)
    get_street_view_images(42.350148, -71.069929, radius=100, api_key=api_key,
                           lat_range=1, lng_range=1, coord_prec=0.001, zoom_level=3)
