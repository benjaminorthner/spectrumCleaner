"""
Created on May 11 2023

@author: Benjamin Orthner (based on Code by @Alex)
"""

from collections import OrderedDict
import numpy as np
import os
import shutil

class SifConverter():
    def __init__(self) -> None:
        self._MAGIC = 'Andor Technology Multi-Channel File\n'
    
    # TODO TEST THIS FUNCTION (idk about the following, maybe keep it simple for now) AND ADD THAT IF SIF FILE IS ALREADY IN SIF FOLDER THEN TXT GETS MOVES OUT AND SIF DOES NOT MOVE
    def convert(self, filePath) -> str:
        '''convert a single file from .sif to .txt and return path of out file'''

        conversionSuccess = True

        # try converting file
        try: 
            #extract data from sif
            x, y, vals = self.get_xy_fromsif(filePath)
            
            # write data to txt file
            out = []
            for j in range(len(vals[0])):
                out.append([vals[0][j],vals[1][j][1]])
            
            
            for j in range(len(x)):
                out.append([x[j],y[j]])
        
            
            out_file=filePath+"_conv.txt"
            with open(out_file, 'w') as f:
                for item in out:
                    f.write(str(item[0])+"\t"+str(item[1])+"\n")
        
            # if sif folder does not exist, then create it
            sif_folder = os.path.join(os.path.dirname(filePath), "sif")
            if not os.path.exists(sif_folder):
                os.mkdir(sif_folder)

            # move the sif file to the sif folder
            shutil.move(filePath, sif_folder)

        # if conversion fails 
        except:
            conversionSuccess == False
            out_file = ""

        return conversionSuccess, out_file


    # display how many files successfully converted. how many skipped and how many failed to convert
    def batchConvert(self, folderPath):
        '''recursively converts a folder tree from sif to txt'''

        stats = {"successes":0, "failures": 0, "skipped": 0}

        # recursively traverse all subdirectories of the folderPath
        for root, dirs, files in os.walk(folderPath):

            # check if the current folder is called "sif" and if yes, skip this folder and its files
            if os.path.basename(root) == "sif":
                stats['skipped'] += len(files)
                continue

            # for each file with .sif extension convert them to .txt
            for file in files:
                if file.endswith('.sif'):
                    file_path = os.path.join(root, file)
                    conversionSuccess, _ = self.convert(file_path)

                    if conversionSuccess:
                        stats['successes'] += 1
                    else:
                        stats['failures'] += 1

        print("ConversionStats: ", stats) 

    def failedToConvert(self):
        '''displays error when conversion fails'''
        print("FAILED TO CONVERT")

    def _to_string(self, c):
        ''' convert bytes to string. c: string or bytes'''
        return c if not isinstance(c, bytes) else c.decode('utf-8')

    def _read_string(self, fp, length = None):
        '''Read a string of the given length. If no length is provided, the
        length is read from the file.'''
        if length is None:
            length = int(self._to_string(fp.readline()))
        return fp.read(length)

    def _read_until(self, fp, terminator=' '):
        '''Read a space-delimited word.'''
        word = ''
        while True:
            c = self._to_string(fp.read(1))
            if c == terminator or c == '\n':
                if len(word) > 0:
                    break
            word += c
        return word

    def _read_int(self, fp):
        return int(self._read_until(fp, ' '))

    def _read_float(self, fp):
        return float(self._read_until(fp, ' '))

    def _open(self, fp):
        """
        A helper function to read SIF file.

        Parameters
        -----------
        fp: File pointing to SIF file

        Returns
        -------
        tile: list
            A list of tuples, that contains the image location in the file.
        size: a tuple, (wdith, height)
        n_frames: integer
            number of frames
        info: dict
            Dictionary containing misc data.
        """
        info = OrderedDict()

        if self._to_string(fp.read(36)) != self._MAGIC:
            raise SyntaxError('not a SIF file')

        # What's this?
        fp.readline() # 65538 number_of_images?

        info['SifVersion'] = int(self._read_until(fp, ' ')) # 65559

        # What's this?
        self._read_until(fp, ' ') # 0
        self._read_until(fp, ' ') # 0
        self._read_until(fp, ' ') # 1

        info['ExperimentTime'] = self._read_int(fp)
        info['DetectorTemperature'] = self._read_float(fp)

        # What is this?
        self._read_string(fp, 10) # blank

        # What is this?
        self._read_until(fp, ' ') # 0

        info['ExposureTime'] = self._read_float(fp)
        info['CycleTime'] = self._read_float(fp)
        info['AccumulatedCycleTime'] = self._read_float(fp)
        info['AccumulatedCycles'] = self._read_int(fp)

        fp.read(1) # NULL
        fp.read(1) # space

        info['StackCycleTime'] = self._read_float(fp)
        info['PixelReadoutTime'] = self._read_float(fp)

        # What is this?
        self._read_until(fp, ' ') # 0
        self._read_until(fp, ' ') # 1
        info['GainDAC'] = self._read_float(fp)

        # What is the rest of the line?
        self._read_until(fp, '\n')

        info['DetectorType'] = self._to_string(fp.readline())
        info['DetectorDimensions'] = (self._read_int(fp), self._read_int(fp))
        info['OriginalFilename'] = self._read_string(fp)

        # What is this?
        fp.read(2) # space newline

        # What is this?
        self._read_int(fp) # 65538
        info['user_text'] = self._read_string(fp)

        fp.read(1) # newline
        self._read_int(fp) # 65538
        fp.read(8) # 0x01 space 0x02 space 0x03 space 0x00 space
        info['ShutterTime'] = (self._read_float(fp), self._read_float(fp)) # ends in newline

        if (65548 <= info['SifVersion'] &
                info['SifVersion'] <= 65557):
            for _ in range(2):
                fp.readline()
        elif info['SifVersion'] == 65558:
            for _ in range(5):
                fp.readline()
        elif info['SifVersion'] == 65559:
            for _ in range(9):
                fp.readline()
        elif info['SifVersion'] == 65565:
            for _ in range(15):
                fp.readline()
        elif info['SifVersion'] > 65565:
            for _ in range(18):
                fp.readline()

        info['SifCalbVersion'] = int(self._read_until(fp, ' ')) # 65539
        # additional skip for this version
        if info['SifCalbVersion'] == 65540:
            fp.readline()

        # 4th-order polynomial coefficients
        info['Calibration_data'] = fp.readline()

        fp.readline() # 0 1 0 0 newline
        fp.readline() # 0 1 0 0 newline
        fp.readline() # 0 1 0 0 newline

        fp.readline() # 422 newline or 433 newline

        fp.readline() # 13 newline
        fp.readline() # 13 newline

        info['FrameAxis'] = self._read_string(fp)
        info['DataType'] = self._read_string(fp)
        info['ImageAxis'] = self._read_string(fp)

        self._read_until(fp, ' ') # 65541

        self._read_until(fp, ' ') # x0? left? -> x0
        self._read_until(fp, ' ') # x1? bottom? -> y1
        self._read_until(fp, ' ') # y1? right? -> x1
        self._read_until(fp, ' ') # y0? top? -> y0

        no_images = int(self._read_until(fp, ' '))
        no_subimages = int(self._read_until(fp, ' '))
        total_length = int(self._read_until(fp, ' '))
        image_length = int(self._read_until(fp, ' '))
        info['NumberOfFrames'] = no_images

        for i in range(no_subimages):
            # read subimage information
            self._read_until(fp, ' ') # 65538

            frame_area = fp.readline().strip().split()
            x0, y1, x1, y0, ybin, xbin = map(int,frame_area[:6])
            width = int((1 + x1 - x0) / xbin)
            height = int((1 + y1 - y0) / ybin)
        size = (int(width), int(height) * no_subimages)
        tile = []

        for f in range(no_images):
            info['timestamp_of_{0:d}'.format(f)] = int(fp.readline())

        offset = fp.tell()
        try: # remove extra 0 if it exits.
            flag = int(fp.readline())
            if flag == 0:
                offset = fp.tell()
            # remove another extra 1
            if flag == 1:
                fp.readline()
                offset = fp.tell()
        except:
            fp.seek(offset)

        for f in range(no_images):
            tile.append(("raw", (0, 0) + size,
                        offset + f * width * height * no_subimages * 4,
                        ('F;32F', 0, 1)))

        info = self.extract_user_text(info)

        return tile, size, no_images, info


    def extract_user_text(self, info):
        """
        Extract known information from info['user_text'].
        Current known info is
        + 'Calibration data for frame %d'
        """
        user_text = info['user_text']
        if b'Calibration data for' in user_text[:20]:
            texts = user_text.split(b'\n')
            for i in range(info['NumberOfFrames']):
                key = 'Calibration_data_for_frame_{:d}'.format(i+1)
                coefs = texts[i][len(key)+2:].strip().split(b',')
                info[key] = [float(c) for c in coefs]
            # Calibration data should be None for this case
            info['Calibration_data'] = None
        else:
            coefs = info['Calibration_data'].strip().split()
            try:
                info['Calibration_data'] = [float(c) for c in coefs]
            except ValueError:
                del info['Calibration_data']
        del info['user_text']
        return info

    def np_open(self, sif_file):
        """
        Open sif_file and return as np.array.
        """

        f = open(sif_file,'rb')
        tile, size, no_images, info = self._open(f)

        # allocate np.array
        data = np.ndarray((no_images, size[1], size[0]), dtype=np.float32)
        for i, tile1 in enumerate(tile):
            f.seek(tile1[2])  # offset
            data[i] = np.fromfile(f, count=size[0]*size[1],dtype='<f').reshape(size[1],size[0])

        try:
            f.close()
        finally:
            pass

        return data, info

    def get_xy_fromsif(self, file):
            dat=self.np_open(file)
            calib=dat[1]["Calibration_data"]
            y=dat[0][0][0]   
            x=np.arange(len(y)+1)[1:]
            x=calib[0]+x*calib[1]+x**2*calib[2]+x**3*calib[3]
            vals=[list(dat[1].keys()),list(dat[1].items())]
            return(x,y,vals)