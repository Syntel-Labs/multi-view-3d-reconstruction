import cv2 as cv

def orb_pipeline(frontal, side, nfeatures=1500, ratio=0.75):
    """
    Pipeline ORB para detección y matching de features.

    Args:
        frontal: imagen 1
        side: imagen 2
        nfeatures: número de features ORB
        ratio: umbral para Lowe's ratio test

    Returns:
        Imagen con matches dibujados
    """

    orb = cv.ORB_create(nfeatures=nfeatures)

    kp1, des1 = orb.detectAndCompute(frontal, None)
    kp2, des2 = orb.detectAndCompute(side, None)

    if des1 is None or des2 is None:
        raise ValueError("No se pudieron detectar descriptores en alguna imagen")

    bf = cv.BFMatcher(cv.NORM_HAMMING, crossCheck=False)
    matches = bf.knnMatch(des1, des2, k=2)

    good = []
    for m, n in matches:
        if m.distance < ratio * n.distance:
            good.append([m])

    matched_image = cv.drawMatchesKnn(
        frontal,
        kp1,
        side,
        kp2,
        good,
        None,
        flags=cv.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS
    )

    return matched_image
