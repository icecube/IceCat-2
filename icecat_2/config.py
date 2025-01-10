import os

class config:

    baseline_gcd_path   = '/data/user/followup/baseline_gcds/'
    splines_tables_path = '/cvmfs/icecube.opensciencegrid.org/data/photon-tables/splines/'

    te_orig_threshold   = 50000 ## GeV

    workdir             = '/data/user/azegarelli/IceCat-2/'

    alerts_table_dir    = workdir+'/docs/'
    i3files_dir         = workdir+'/icecat_2/output/'
    # Create the folder if it doesn't exist
    if not os.path.exists(i3files_dir):
        os.makedirs(i3files_dir)
