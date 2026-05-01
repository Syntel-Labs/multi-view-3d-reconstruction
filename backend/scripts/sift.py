"""Script de uso unico: prueba de pipeline SIFT con matching y Lowe ratio test."""

import cv2 as cv


def sift_pipeline(frontal, side, nfeatures=0, ratio=0.75):
    """Pipeline SIFT para deteccion y matching de features.

    Args:
        frontal: imagen 1 (array BGR o grises)
        side: imagen 2 (array BGR o grises)
        nfeatures: numero maximo de features a retener (0 = todos)
        ratio: umbral para Lowe ratio test

    Returns:
        Imagen con matches dibujados
    """
    sift = cv.SIFT_create(nfeatures=nfeatures)

    kp1, des1 = sift.detectAndCompute(frontal, None)
    kp2, des2 = sift.detectAndCompute(side, None)

    if des1 is None or des2 is None:
        raise ValueError("No se pudieron detectar descriptores en alguna imagen")

    bf = cv.BFMatcher(cv.NORM_L2, crossCheck=False)
    matches = bf.knnMatch(des1, des2, k=2)

    good = []
    for m, n in matches:
        if m.distance < ratio * n.distance:
            good.append([m])

    return cv.drawMatchesKnn(
        frontal,
        kp1,
        side,
        kp2,
        good,
        None,
        flags=cv.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS,
    )
