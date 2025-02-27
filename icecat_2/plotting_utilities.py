import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import healpy as hp
import config
import re
import pickle

cfg = config.config()

def angular_distance(lon1, lat1, lon2, lat2):
    c1 = np.cos(lat1)
    c2 = np.cos(lat2)
    s1 = np.sin(lat1)
    s2 = np.sin(lat2)
    sd = np.sin(lon2 - lon1)
    cd = np.cos(lon2 - lon1)

    return np.arctan2(
        np.hypot(c2 * sd, c1 * s2 - s1 * c2 * cd),
        s1 * s2 + c1 * c2 * cd
    )


# Calculates are using Gauss-Green theorem / shoelace formula
# TODO: vectorize using numpy.
# Note: in some cases the argument is not a np.ndarray so one has
# to convert the data series beforehand.
def calculate_area(vs) -> float:
    
    a = 0
    y0, x0 = vs[0]
    for [y1, x1] in vs[1:]:
        dx = np.cos(x1)-np.cos(x0)
        dy = y1-y0
        a += 0.5*(y0*dx - np.cos(x0)*dy)
        x0 = x1
        y0 = y1
        
    return a

def calculate_contour_areas_from_pkl(f):

    with open(f, "rb") as f:
        data = pickle.load(f)
    conts50 = data[0]
    conts90 = data[1]
    area50 = 0.
    area90 = 0.
    mean_ra = 0.
    for i, cont in enumerate(conts50):
        cont = np.array(cont)
        if(i==0):
            ras_first_contour = cont[:,0]
            mean_ra = np.mean(ras_first_contour)   
        #cont = np.array(cont)
        cont[:,1] = np.pi/2. - cont[:,1]
        cont[:,0] += np.pi-mean_ra
        cont[:,0] %= 2*np.pi
        area50 += abs(calculate_area(cont))
    for i, cont in enumerate(conts90):
        cont = np.array(cont)
        if(i==0):
            ras_first_contour = cont[:,0]
            mean_ra = np.mean(ras_first_contour)
        cont[:,1] = np.pi/2. - cont[:,1]
        cont[:,0] += np.pi-mean_ra
        cont[:,0] %= 2*np.pi
        area90 += abs(calculate_area(cont))
    area50 = abs(area50)*180.*180./(np.pi*np.pi)
    area90 = abs(area90)*180.*180./(np.pi*np.pi)
    return area50, area90

def llh2area(llhlevel):
    # Ensure skymap values are finite (not NaN or Inf)
    valid_mask = np.isfinite(skymap)  # This will return True for finite values (not NaN or Inf)
    # Apply the mask to filter out invalid pixels
    valid_skymap = skymap[valid_mask]
    npix_tot = np.sum(skymap <= llhlevel)
    npix = np.sum(valid_skymap <= llhlevel)
    return npix*pixarea

def calculate_countour_areas_from_fits(f):

    global skymap
    global pixarea
    skymap, header = hp.read_map(f,h=True)
    comments = next((value for key, value in header if key == 'COMMENTS'), None)
    '''
    substring = 'Change in 2LLH of 22.2(64.2)'
    if(comments=="50%(90%) uncertainty location => Change in 2LLH of 22.2(64.2)"):
        llh50 = 22.2
        llh90 = 64.2
    else:
        print(comments)
        llh50 = 1.39
        llh90 = 4.61   
    '''
    if comments.find(substring) != -1:
        #print("Pattern found!")
        # Use regex to extract both numbers (the one before and inside the parentheses)
        matches = re.findall(r"(\d+\.\d+)(?:\((\d+\.\d+)\))?", comments) # 50%(90%) uncertainty location => Change in 2LLH of 22.2(64.2)
        print(matches)
        # Flatten the matches and convert them to float
        values = [float(num) for match in matches for num in match if num]
        llh50 = values[0]
        llh90 = values[1]
    else:
        llh50 = 1.39
        llh90 = 4.61
    
    npix = len(skymap)
    nside = hp.npix2nside(npix)
    pixarea = hp.nside2pixarea(nside, degrees=True)
    area90 = llh2area(llh90)
    area50 = llh2area(llh50)
    #print(area50,area90)
    return area50, area90
