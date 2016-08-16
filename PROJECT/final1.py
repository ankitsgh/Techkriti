import cv2
import numpy as np
import cv
import sys
import os
sys.path.append("/home/ankit/yael_v438/yael")
import ynumpy
import subprocess
refPt = []
j=0
t=0
counter=0
sk=0
cropping = False
drag=0
img=[]
trajs = []
hogs = []
hofs = []
mbhxs = []
mbhys = []
imgy=[]
text=""
vpath='/home/ankit/r/test.mp4'
outputdir = '/home/ankit/r/out.features.gz'

def make_gmm(bm):
 bm = bm.astype('float32')
 mean = bm.mean(axis = 0)
 bm = bm - mean
 gmm = ynumpy.gmm_learn(bm,120)
 finale = (gmm,mean,None)
 return finale
 
def reads(ll):
 global trajs,hofs,mbhxs,mbhys,hogs

 frameNum = int(ll[0])
 mean_x = float(ll[1])
 mean_y = float(ll[2])
 var_x = float(ll[3])
 var_y = float(ll[4])
 length = float(ll[5])
 scale = float(ll[6])
 x_pos = float(ll[7])
 y_pos = float(ll[8])
 t_pos = float(ll[9])
 traj_start =10
 hog_start = traj_start + 30
 hof_start = hog_start + 96
 mbhx_start = hof_start + 108
 mbhy_start = mbhx_start + 96
 mbhy_end = mbhy_start + 96
 traj = [float(l) for l in ll[traj_start:hog_start]]
 hog = [float(l) for l in ll[hog_start:hof_start]]
 hof = [float(l) for l in ll[hof_start:mbhx_start]]
 mbhx = [float(l) for l in ll[mbhx_start:mbhy_start]]
 mbhy = [float(l) for l in ll[mbhy_start:mbhy_end]]
 
 trajs.append(np.ndarray(shape=(1,30), buffer=np.array(traj),dtype=float))
 hogs.append(np.ndarray(shape=(1,96), buffer=np.array(hog),dtype=float))
 hofs.append(np.ndarray(shape=(1,108), buffer=np.array(hof),dtype=float))
 mbhxs.append(np.ndarray(shape=(1,96), buffer=np.array(mbhx),dtype=float))
 mbhys.append(np.ndarray(shape=(1,96), buffer=np.array(mbhy),dtype=float))
def fishy(path):
 f=open(path,"r")
 global trajs,hofs,mbhxs,mbhys,counter,hogs
 trajs = []
 hogs = []
 hofs = []
 mbhxs = []
 mbhys = []

 for line in f:
    ll = line.strip().split()
    reads(ll)
 traje = np.vstack(trajs)
 hoge = np.vstack(hogs)
 hofe = np.vstack(hofs)
 mbhxe = np.vstack(mbhxs)
 mbhye = np.vstack(mbhys)
 bm_list = []
 bm_list.append(np.vstack(trajs))
 bm_list.append(np.vstack(hogs))
 bm_list.append(np.vstack(hofs))
 bm_list.append(np.vstack(mbhxs))
 bm_list.append(np.vstack(mbhys))
 gmm_list = [make_gmm(bm) for bm in bm_list]
 np.savez(('gmm'+str(counter)), gmm_list=gmm_list)

 fvs = []
 for descriptor,gmm_mean_pca in zip(bm_list,gmm_list):
      gmm, mean, pca_transform = gmm_mean_pca
      descrip = descriptor.astype('float32') - mean
      if pca_transform != None:
        descrip = np.dot(descriptor.astype('float32') - mean, pca_transform)
      fv = ynumpy.fisher(gmm, descrip, include = ['mu', 'sigma'])
      fv = np.sign(fv) * (np.abs(fv) ** 0.5)
      norms = np.sqrt(np.sum(fv ** 2))
      fv /= norms
      fv[np.isnan(fv)] = 100
      fvs.append(fv.T)
 output_fv = np.hstack(fvs)


 norm = np.sqrt(np.sum(output_fv ** 2))
 output_fv /= norm


 np.savez(('fish'+str(counter)), fish=output_fv)
def click_and_crop(event, x, y, flags, param):
 global refPt, cropping,j,img,drag,t
 if event == cv2.EVENT_LBUTTONDOWN and not drag:
    refPt = [(x, y)]
    drag = 1
 elif event == cv2.EVENT_LBUTTONUP and drag:
    refPt.append((x, y))
    print "r"
    imgy = img[refPt[0][1]:refPt[1][1], refPt[0][0]:refPt[1][0]]
    t=1
    drag=0
 elif event == cv2.EVENT_MOUSEMOVE and drag:
    clone = img.copy()
    cv2.rectangle(clone, refPt[0], (x,y), (0, 255, 0), 2)
    cv2.imshow("image",clone)

path_n='/home/ankit/fishers'
paths = [os.path.join(path_n, f) for f in sorted(os.listdir(path_n))]
matrix=[]
target=[]
label=[1.0,1.0,1.0,1.0,1.0,2.0,2.0,2.0,2.0,2.0,3.0,3.0,3.0,3.0,3.0,4.0,4.0,4.0,4.0,4.0,5.0,5.0,5.0,5.0,5.0]#1 for angry 2for fear 3 happy 4 normal 5 sad
i=0
for path in paths:
 print path
 matrix.append((np.load(path))['fish'])
 target.append(label[i])
 i=i+1
X_train=np.vstack(matrix)
Y_train=np.array(target)
j=0
mov=cv2.VideoCapture(0)
while(mov.isOpened()):
 
 cv2.namedWindow("image")

 while True:
  ret, img = mov.read()
  if len(refPt) == 2:
        j=j+1
	imgy = img[refPt[0][1]:refPt[1][1], refPt[0][0]:refPt[1][0]]
        cv2.rectangle(img, refPt[0], refPt[1], (0, 255, 0),2)
        cv2.imwrite("test"+str(j)+".png",imgy)
        font=cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(img,text,(10,500),font,4,(255,255,255),2)
        cv2.imshow("image1",imgy)
  if t==0:
    cv2.setMouseCallback("image", click_and_crop)  
  cv2.imshow("image",img)
  k = cv2.waitKey(100) & 0xff
  if k == 27:
    break
  if(j%60==0 and j>=1):
   j=1
   counter=counter+1
   cmd='/home/ankit/ffmpeg-0.11.1/ffmpeg -r 10 -f image2 -s 1920x1080 -i test%d.png  -pix_fmt yuv420p '+str(counter)+'test.mp4'
   subprocess.call(cmd,shell='True')
   dpath='/home/ankit/improved_trajectory_release/release/DenseTrackStab /home/ankit/PROJECT/'+str(counter)+'test.mp4 | gzip > '+str(counter)+'out.features.gz'
   subprocess.call(dpath, shell=True)
   subprocess.call('gzip -d '+str(counter)+'out.features.gz', shell=True)
   fishy(str(counter)+'out.features')
   matrix=[]
   matrix.append((np.load('fish'+str(counter)+'.npz'))['fish'])
   X_test=np.vstack(matrix)
   svm_params = dict( kernel_type = cv2.SVM_LINEAR,
                svm_type = cv2.SVM_C_SVC,
                C=2.67, gamma=5.383 )

   trainData=np.float32(X_train)
   responses=np.float32(Y_train)
   svm = cv2.SVM()
   svm.train(trainData,responses, params=svm_params)
   faceFloat = np.float32(X_test)
   result = svm.predict(faceFloat, True)
   print result
   if result==4.0:
    text="normal"
   if result==3.0:
     text="happy"
   if result==2.0:
    text="fear"
   if result==1.0:
    text="angry"
   if result==5.0:
    text="sad"




cv2.destroyAllWindows()
mov.release()
 




