import requests
import os
import sys

BASE_URL = "http://127.0.0.1:8000/api/complaints"

def test_image_upload_workflow():
    print("=" * 70)
    print("TESTING IMAGE UPLOADER & COMPLAINT WORKFLOW")
    print("=" * 70)

    # 1. Create a dummy test image
    test_img_path = "temp_test_evidence.jpg"
    with open(test_img_path, "wb") as f:
        f.write(b"\xFF\xD8\xFF\xE0\x00\x10JFIF" + b"\x00" * 500) # minimal dummy JPG file

    try:
        # 2. Test upload endpoint
        print("\n[Step 1]: Uploading image to /api/complaints/upload-image...")
        with open(test_img_path, "rb") as f:
            files = {"file": ("test_pothole.jpg", f, "image/jpeg")}
            res = requests.post(f"{BASE_URL}/upload-image", files=files)
        
        print(f"Upload Response Status Code: {res.status_code}")
        print(f"Upload Response Payload: {res.json()}")
        assert res.status_code == 200, f"Expected 200, got {res.status_code}"
        upload_data = res.json()
        image_url = upload_data["image_url"]
        assert image_url.startswith("/uploads/"), "image_url should start with /uploads/"
        print("✓ Image uploaded successfully!")

        # 3. Test submitting complaint with uploaded image URL
        print("\n[Step 2]: Submitting complaint with uploaded image URL...")
        payload = {
            "citizen_name": "Test Citizen",
            "citizen_email": "test.citizen@example.com",
            "location": "MG Road, Ward 12",
            "description": "Deep crater pothole in the middle of flyover ramp causing two-wheelers to crash.",
            "image_url": image_url
        }
        res2 = requests.post(f"{BASE_URL}/", json=payload)
        print(f"Complaint Submission Status Code: {res2.status_code}")
        comp_data = res2.json()
        print(f"Complaint ID: {comp_data['complaint_id']}")
        print(f"Stored Image URL: {comp_data['image_url']}")
        assert comp_data["image_url"] == image_url, "Image URL must match uploaded path"
        print("✓ Complaint created with image evidence in SQLite!")

        # 4. Test searching complaints to verify admin dashboard data
        print("\n[Step 3]: Fetching complaints via /search for Admin Dashboard...")
        res3 = requests.get(f"{BASE_URL}/search")
        complaints_list = res3.json()
        matched = [c for c in complaints_list if c["complaint_id"] == comp_data["complaint_id"]]
        assert len(matched) == 1, "Submitted complaint must be retrievable in search"
        print(f"Found complaint in admin list! Image evidence URL: {matched[0]['image_url']}")
        print("✓ Evidence visible in Admin Dashboard API response!")

        # 5. Test file validation (e.g. invalid extension or empty file)
        print("\n[Step 4]: Testing validation errors (invalid format & empty file)...")
        dummy_txt = "invalid.txt"
        with open(dummy_txt, "w") as f:
            f.write("text content")

        with open(dummy_txt, "rb") as f:
            files_invalid = {"file": ("test.txt", f, "text/plain")}
            res_val = requests.post(f"{BASE_URL}/upload-image", files=files_invalid)
        
        print(f"Invalid file response status: {res_val.status_code}")
        print(f"Invalid file error message: {res_val.json()}")
        assert res_val.status_code == 400, "Should return 400 for invalid file extension"
        print("✓ Validation logic correctly rejected invalid file type!")

    finally:
        # Cleanup temporary test files
        if os.path.exists(test_img_path):
            os.remove(test_img_path)
        if os.path.exists("invalid.txt"):
            os.remove("invalid.txt")

    print("\n" + "=" * 70)
    print("ALL WORKFLOW TESTS PASSED PERFECTLY!")
    print("=" * 70)

if __name__ == "__main__":
    test_image_upload_workflow()
