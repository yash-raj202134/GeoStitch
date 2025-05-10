import cv2
import numpy as np
import matplotlib.pyplot as plt
import glob
import os

# Crop function to remove black borders
def crop_black(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 1, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if contours:
        x, y, w, h = cv2.boundingRect(contours[0])
        return image[y:y+h, x:x+w]
    return image

# Warping and stitching function
def warpImages(img1, img2, H):
    rows1, cols1 = img1.shape[:2]
    rows2, cols2 = img2.shape[:2]

    points1 = np.float32([[0,0], [0,rows1], [cols1,rows1], [cols1,0]]).reshape(-1,1,2)
    points2 = np.float32([[0,0], [0,rows2], [cols2,rows2], [cols2,0]]).reshape(-1,1,2)
    points2_ = cv2.perspectiveTransform(points2, H)
    points = np.concatenate((points1, points2_), axis=0)

    [xmin, ymin] = np.int32(points.min(axis=0).ravel() - 0.5)
    [xmax, ymax] = np.int32(points.max(axis=0).ravel() + 0.5)
    translation = [-xmin, -ymin]

    H_translation = np.array([
        [1, 0, translation[0]],
        [0, 1, translation[1]],
        [0, 0, 1]
    ])

    result = cv2.warpPerspective(img2, H_translation @ H, (xmax - xmin, ymax - ymin))
    result[translation[1]:translation[1]+rows1, translation[0]:translation[0]+cols1] = img1
    return result

# Stitching function
def stitch_pair(img1, img2):
    gray1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
    gray2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)

    kp1, des1 = sift.detectAndCompute(gray1, None)
    kp2, des2 = sift.detectAndCompute(gray2, None)

    if des1 is None or des2 is None:
        print("⚠️ Feature detection failed.")
        return img1

    matches = bf.knnMatch(des1, des2, k=2)
    good = [m for m, n in matches if m.distance < 0.75 * n.distance]

    if len(good) > 10:
        src_pts = np.float32([kp1[m.queryIdx].pt for m in good]).reshape(-1, 1, 2)
        dst_pts = np.float32([kp2[m.trainIdx].pt for m in good]).reshape(-1, 1, 2)
        M, _ = cv2.findHomography(dst_pts, src_pts, cv2.RANSAC, 5.0)
        if M is not None:
            try:
                return warpImages(img1, img2, M)
            except cv2.error:
                print("⚠️ Warping failed due to image size.")
                return img1
    print("⚠️ Not enough good matches.")
    return img1

# Load and resize images
image_paths = sorted(glob.glob("output_frames/*.png"))
resize_fx, resize_fy = 0.5, 0.5  # Use higher resolution for better quality

img_list = []
for path in image_paths:
    img = cv2.imread(path)
    if img is not None:
        img = cv2.resize(img, (0, 0), fx=resize_fx, fy=resize_fy)
        img_list.append(img)

# Initialize SIFT and Matcher
sift = cv2.SIFT_create(nfeatures=500)
bf = cv2.BFMatcher()

# Stitch progressively
stitched = img_list[0]
for i in range(1, len(img_list)):
    stitched = stitch_pair(stitched, img_list[i])

# Final crop and show
stitched = crop_black(stitched)
stitched_rgb = cv2.cvtColor(stitched, cv2.COLOR_BGR2RGB)

plt.figure(figsize=(18, 10))
plt.imshow(stitched_rgb)
plt.title("High-Quality Panorama")
plt.axis('off')
plt.tight_layout()
# plt.show()


# Save the final stitched image
output_path = 'stitched_result.png'
cv2.imwrite(output_path, stitched)
print(f"✅ Stitching completed! Saved as: {output_path}")
