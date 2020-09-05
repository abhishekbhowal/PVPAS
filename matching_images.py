import cv2
from matplotlib import pyplot as plt
cv2.ocl.setUseOpenCL(False)

img1 = cv2.imread('test.jpg',0) # training image
blur1 = cv2.GaussianBlur(img1,(5,5),0)
ret1,th1 = cv2.threshold(blur1,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)

img2 = cv2.imread('test.jpg',0) #query image
blur2 = cv2.GaussianBlur(img2,(5,5),0)
ret2,th2 = cv2.threshold(blur2,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)

orb = cv2.ORB_create(nfeatures=500)
bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=False)
kp1, des1 = orb.detectAndCompute(th1,None)
kp2, des2 = orb.detectAndCompute(th2,None)
print len(des1)
print len(des2)
#crossCheck cannot be performed with KNN Matcher
matches = bf.knnMatch(des1,des2,k=2)
print len(matches)
good = []
for m,n in matches:
    if m.distance < 0.9*n.distance:
        good.append([m])
print len(good)
img3 = cv2.drawMatchesKnn(th1,kp1,th2,kp2,good,None,flags=2)
plt.imshow(img3)
plt.show()
