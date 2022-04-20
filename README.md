# FishImages
Two-Photon-Microscope Images of fish (.lif data) with known y-Overlap and unknown x-Axis shift and unkown amount of pictures per Fish. 
Data needed to be processed first:

Read In lifs <br />
Unpack Lifs in lists in lists so as every entry is all Images of  the same segment<br />
Make one picture out of the z_stacks<br />
Make list with every entry corresponding to one fish<br />
Delete Noise and noramlize Values in all pictures<br />
Take on fish at a time and calculated for every segment the x-axis shift<br />
Done with comparison of Cut Images with no overlap<br />
Shift images with np.roll<br />
Fuse Uncut Images with gradient <br />
Use Lut to make Image Green<br />
Save as bmp<br />
