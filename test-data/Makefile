#!/usr/bin/make

download: CT-MONO2-16-ankle.png
	wget http://deanvaughan.org/projects/dicom_samples/CT-MONO2-16-ankle.dcm
	dcm2hdr.py CT-MONO2-16-ankle.dcm CT-MONO2-16-ankle.png
	dcm2hdr.py CT-MONO2-16-ankle.dcm CT-MONO2-16-ankle.tiff
