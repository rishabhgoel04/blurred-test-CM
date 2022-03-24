import sys, cv2, requests
import numpy as np
import math as m
from libsvm.svmutil import *
import svmutil
# from svm import *
# from svmutil import *

from helper import *
from import_modules import *
from scipy.special import gamma as tgamma


sys.path.append('ImageMetrics/Python/libsvm/python')
sys.path.append('ImageMetrics/Python/libsvm/python/svm.py')
sys.path.append('ImageMetrics/Python/libsvm/python/svmutil.py')

def run():
    df=pd.read_csv("data.csv")
    df=df.iloc[:10]
    # df=get_data_cmdb("""
    # select oi.sku_id,  p.product_name_en, oi.product_image
    # from order_items oi
    # left join products p on oi.sku_id=p.sku_id and oi.catalogue_name=p.catalogue_name
    # group by 1,2,3 limit 100""")

    # In[16]:
    def AGGDfit(structdis):
        # variables to count positive pixels / negative pixels and their squared sum
        poscount = 0
        negcount = 0
        possqsum = 0
        negsqsum = 0
        abssum   = 0

        poscount = len(structdis[structdis > 0]) # number of positive pixels
        negcount = len(structdis[structdis < 0]) # number of negative pixels
        
        # calculate squared sum of positive pixels and negative pixels
        possqsum = np.sum(np.power(structdis[structdis > 0], 2))
        negsqsum = np.sum(np.power(structdis[structdis < 0], 2))
        
        # absolute squared sum
        abssum = np.sum(structdis[structdis > 0]) + np.sum(-1 * structdis[structdis < 0])

        # calculate left sigma variance and right sigma variance
        lsigma_best = np.sqrt((negsqsum/negcount))
        rsigma_best = np.sqrt((possqsum/poscount))

        gammahat = lsigma_best/rsigma_best
        
        # total number of pixels - totalcount
        totalcount = structdis.shape[1] * structdis.shape[0]

        rhat = m.pow(abssum/totalcount, 2)/((negsqsum + possqsum)/totalcount)
        rhatnorm = rhat * (m.pow(gammahat, 3) + 1) * (gammahat + 1)/(m.pow(m.pow(gammahat, 2) + 1, 2))
        
        prevgamma = 0
        prevdiff  = 1e10
        sampling  = 0.001
        gam = 0.2

        # vectorized function call for best fitting parameters
        vectfunc = np.vectorize(func, otypes = [np.float], cache = False)
        
        # calculate best fit params
        gamma_best = vectfunc(gam, prevgamma, prevdiff, sampling, rhatnorm)

        return [lsigma_best, rsigma_best, gamma_best] 


    def func(gam, prevgamma, prevdiff, sampling, rhatnorm):
        while(gam < 10):
            r_gam = tgamma(2/gam) * tgamma(2/gam) / (tgamma(1/gam) * tgamma(3/gam))
            diff = abs(r_gam - rhatnorm)
            if(diff > prevdiff): break
            prevdiff = diff
            prevgamma = gam
            gam += sampling
        gamma_best = prevgamma
        return gamma_best

    def compute_features(img):
        scalenum = 2
        feat = []
        # make a copy of the image 
        im_original = img.copy()

        # scale the images twice 
        for itr_scale in range(scalenum):
            im = im_original.copy()
            # normalize the image
            im = im / 255.0

            # calculating MSCN coefficients
            mu = cv2.GaussianBlur(im, (7, 7), 1.166)
            mu_sq = mu * mu
            sigma = cv2.GaussianBlur(im*im, (7, 7), 1.166)
            sigma = (sigma - mu_sq)**0.5
            
            # structdis is the MSCN image
            structdis = im - mu
            structdis /= (sigma + 1.0/255)
            
            # calculate best fitted parameters from MSCN image
            best_fit_params = AGGDfit(structdis)
            # unwrap the best fit parameters 
            lsigma_best = best_fit_params[0]
            rsigma_best = best_fit_params[1]
            gamma_best  = best_fit_params[2]
            
            # append the best fit parameters for MSCN image
            feat.append(gamma_best)
            feat.append((lsigma_best*lsigma_best + rsigma_best*rsigma_best)/2)

            # shifting indices for creating pair-wise products
            shifts = [[0,1], [1,0], [1,1], [-1,1]] # H V D1 D2

            for itr_shift in range(1, len(shifts) + 1):
                OrigArr = structdis
                reqshift = shifts[itr_shift-1] # shifting index

                # create transformation matrix for warpAffine function
                M = np.float32([[1, 0, reqshift[1]], [0, 1, reqshift[0]]])
                ShiftArr = cv2.warpAffine(OrigArr, M, (structdis.shape[1], structdis.shape[0]))
                
                Shifted_new_structdis = ShiftArr
                Shifted_new_structdis = Shifted_new_structdis * structdis
                # shifted_new_structdis is the pairwise product 
                # best fit the pairwise product 
                best_fit_params = AGGDfit(Shifted_new_structdis)
                lsigma_best = best_fit_params[0]
                rsigma_best = best_fit_params[1]
                gamma_best  = best_fit_params[2]

                constant = m.pow(tgamma(1/gamma_best), 0.5)/m.pow(tgamma(3/gamma_best), 0.5)
                meanparam = (rsigma_best - lsigma_best) * (tgamma(2/gamma_best)/tgamma(1/gamma_best)) * constant

                # append the best fit calculated parameters            
                feat.append(gamma_best) # gamma best
                feat.append(meanparam) # mean shape
                feat.append(m.pow(lsigma_best, 2)) # left variance square
                feat.append(m.pow(rsigma_best, 2)) # right variance square
            
            # resize the image on next iteration
            im_original = cv2.resize(im_original, (0,0), fx=0.5, fy=0.5, interpolation=cv2.INTER_CUBIC)
        return feat


    def test_measure_BRISQUE(dis):
        # read image from given path
    #     dis = cv2.imread(imgPath, 1)
    #     if(dis is None):
    #         print("Wrong image path given")
    #         print("Exiting...")
    #         sys.exit(0)
    #     # convert to gray scale
        dis = cv2.cvtColor(dis, cv2.COLOR_BGR2GRAY)

        # compute feature vectors of the image
        features = compute_features(dis)

        # rescale the brisqueFeatures vector from -1 to 1
        x = [0]
        
        # pre loaded lists from C++ Module to rescale brisquefeatures vector to [-1, 1]
        min_= [0.336999 ,0.019667 ,0.230000 ,-0.125959 ,0.000167 ,0.000616 ,0.231000 ,-0.125873 ,0.000165 ,0.000600 ,0.241000 ,-0.128814 ,0.000179 ,0.000386 ,0.243000 ,-0.133080 ,0.000182 ,0.000421 ,0.436998 ,0.016929 ,0.247000 ,-0.200231 ,0.000104 ,0.000834 ,0.257000 ,-0.200017 ,0.000112 ,0.000876 ,0.257000 ,-0.155072 ,0.000112 ,0.000356 ,0.258000 ,-0.154374 ,0.000117 ,0.000351]
        
        max_= [9.999411, 0.807472, 1.644021, 0.202917, 0.712384, 0.468672, 1.644021, 0.169548, 0.713132, 0.467896, 1.553016, 0.101368, 0.687324, 0.533087, 1.554016, 0.101000, 0.689177, 0.533133, 3.639918, 0.800955, 1.096995, 0.175286, 0.755547, 0.399270, 1.095995, 0.155928, 0.751488, 0.402398, 1.041992, 0.093209, 0.623516, 0.532925, 1.042992, 0.093714, 0.621958, 0.534484]

        # append the rescaled vector to x 
        for i in range(0, 36):
            min = min_[i]
            max = max_[i] 
            x.append(-1 + (2.0/(max - min) * (features[i] - min)))
        
        # load model 
        model = svmutil.svm_load_model("ImageMetrics/Python/allmodel")
    #/content/ImageMetrics/Python/allmodel
        # create svm node array from python list
        x, idx = gen_svm_nodearray(x[1:], isKernel=(model.param.kernel_type == PRECOMPUTED))
        x[36].index = -1 # set last index to -1 to indicate the end.
        
        # get important parameters from model
        svm_type = model.get_svm_type()
        is_prob_model = model.is_probability_model()
        nr_class = model.get_nr_class()
        
        if svm_type in (ONE_CLASS, EPSILON_SVR, NU_SVC):
            # here svm_type is EPSILON_SVR as it's regression problem
            nr_classifier = 1
        dec_values = (c_double * nr_classifier)()
        
        # calculate the quality score of the image using the model and svm_node_array
        qualityscore = svmutil.libsvm.svm_predict_probability(model, x, dec_values)

        return qualityscore


    #Cleaning data
    df=df.dropna()
    df.drop_duplicates(subset ="product_image", keep = False, inplace = True)

    #Generating Batches of dataframe in size of 100
    list_df = np.array_split(df, 10)
    print("batches created")
    #Defining the New Dataframe with score
    blurred_df=pd.DataFrame()
    c=0
    for batch_data in list_df:
        blurred_df_batch=pd.DataFrame()
        image_url_list = list(batch_data["product_image"])
        quality_list=[]
        print("batch",c)
        c=c+1
        for image_url in image_url_list:
            
            try:
                resp = requests.get(image_url,headers={'User-Agent': 'Mozilla/5.0'},stream=True).raw
                print("fetched")
            except:
                continue

            try:
                image = np.asarray(bytearray(resp.read()), dtype="uint8")
                image = cv2.imdecode(image, cv2.IMREAD_COLOR)
            except:
                continue
            # print("conv to img")
            # print(image_url)
            if(image is None):
                continue
            else:
                qualityscore = test_measure_BRISQUE(image)
                print("score got")
                
            # try:
            #     qualityscore = test_measure_BRISQUE(image)
            # except:
            #     continue
            h=image.shape[0]
            w=image.shape[1]
            if(qualityscore<50.0) and (h<=900) and (w<=900):
                quality_list.append(qualityscore)
                blurred_df_batch=blurred_df_batch.append(batch_data[batch_data['product_image']==image_url])
                

        blurred_df_batch = blurred_df_batch.assign(score =quality_list)
        # blurred_df_batch=blurred_df_batch.sort_values(by=['score'])
        blurred_df=blurred_df.append(blurred_df_batch,ignore_index=True)
        blurred_df=blurred_df.sort_values(by=['score'])

        print("added in blurred dataframe")
        paste_data_google_sheet(blurred_df,'1gyynC8w82vWzyES9U4ITJusi3obAmdWF3MUWYBl54oM','blurred_sheet',1,1)

