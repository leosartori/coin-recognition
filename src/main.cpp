#include <memory>
#include <iostream>
#include <stdio.h>
// The header files for performing input and output.

#include <opencv2/core.hpp>
#include <opencv2/highgui/highgui.hpp>
// highgui - an interface to video and image capturing.
#include <opencv2/xfeatures2d.hpp>
#include "opencv2/imgproc/imgproc.hpp"
// imgproc - An image processing module that for linear and non-linear  image filtering, geometrical image transformations, color space conversion and so on.
#include <opencv2/ccalib.hpp>
#include <opencv2/stitching.hpp>

using namespace cv;
// Namespace where all the C++ OpenCV functionality resides.

using namespace std;
// For input output operations.

int main()
{
    Mat image;
    // Mat object is a basic image container. image is an object of Mat.

    image = imread("images/1.jpg", CV_LOAD_IMAGE_UNCHANGED);
    // Take any image but make sure its in the same folder.
    // first argument denotes the image to be loaded.
    // second argument specifies the image format as follows:
    // CV_LOAD_IMAGE_UNCHANGED (<0) loads the image as it is.
    // CV_LOAD_IMAGE_GRAYSCALE ( 0) loads the image in Gray scale.
    // CV_LOAD_IMAGE_COLOR (>0) loads the image in the BGR format.
    // If the second argument is not there, it is implied CV_LOAD_IMAGE_COLOR.

    namedWindow("Original", WINDOW_NORMAL);
    imshow("Original", image);

    Mat img_gray;
    cvtColor(image, img_gray, CV_BGR2GRAY);

    // ------------------------ PREPROCESSING ------------------------

    // GAUSSIAN BLUR: reduce noise
    Mat gray_blur;
    GaussianBlur(img_gray, gray_blur, Size(15, 15), 10);
    namedWindow("Blur", WINDOW_NORMAL);
    imshow("Blur", gray_blur);
    waitKey(0);

    Mat thresh;
    // ADAPTIVE THRESHOLDING: divides pixels in above or below variable threshold (black or white)
    // adaptiveThreshold(gray_blur, thresh, 255, ADAPTIVE_THRESH_GAUSSIAN_C, THRESH_BINARY_INV, 11, 1);

    // Otsu thresholding
    cv::threshold(gray_blur, thresh, 0, 255, CV_THRESH_BINARY | CV_THRESH_OTSU);

    namedWindow("Thresh", WINDOW_NORMAL);
    imshow("Thresh", thresh);
    waitKey(0);

    // Closing
    // It is obtained by the dilation of an image followed by an erosion.
    // dst = close( src, element ) = erode( dilate( src, element ) )
    // Useful to remove small holes (dark regions).

    Mat kernel = Mat::ones(3, 3, CV_8U);

    Mat closing;
    morphologyEx(thresh, closing, MORPH_CLOSE, kernel, Point(-1,-1), 10);
    /*
    src	Source image. The number of channels can be arbitrary. The depth should be one of CV_8U, CV_16U, CV_16S, CV_32F or CV_64F.
    dst	Destination image of the same size and type as source image.
    op	Type of a morphological operation, see cv::MorphTypes
    kernel	Structuring element. It can be created using cv::getStructuringElement.
    anchor	Anchor position with the kernel. Negative values mean that the anchor is at the kernel center.
    iterations	Number of times erosion and dilation are applied.
    borderType	Pixel extrapolation method, see cv::BorderTypes
    borderValue	Border value in case of a constant border. The default value has a special meaning.
    */
    namedWindow("Closing", WINDOW_NORMAL);
    imshow("Closing", closing);
    waitKey(0);

    // DEBUG
    // return 0;

    // --------------- CIRCLE DETECTION ----------------------

    // FIND CONTOURS
    /*
    // procedure of finding contours in OpenCV as the operation of finding connected components and their boundaries
    Mat cont_img = closing.clone();
    vector<vector<Point>> contours;
    vector<Vec4i> hierarchy;
    findContours(cont_img, contours, hierarchy, RETR_EXTERNAL, CHAIN_APPROX_NONE);

    for(int i = 0; i < contours.size(); i++){
      double area = contourArea(contours[i]);
      // TODO: remove continue
      if (area < 100)
          continue;

      if (contours[i].size() < 5)
          continue;
      RotatedRect el = fitEllipse(contours[i]);
      ellipse(image, el, Scalar(0,255,0), 3);
    }
    */
    /*
    Note that we made a copy of the closing image because the function
    findContours will change the image passed as the first parameter,
    we’re also using the RETR_EXTERNAL flag, which means that the contours
    returned are only the extreme outer contours.
    The parameter CHAIN_APPROX_SIMPLE will also return a compact
    representation of the contour
    */

    // HOUGH TRANSFORM
    vector<Vec3f> coin;
    // A vector data type to store the details of coins.

    int max_radius = max(image.size().height / 3, image.size().width / 3);

    // OK for more coins with occlusions
    //HoughCircles(closing,coin,CV_HOUGH_GRADIENT,1,50,1000,10,10,0);

    // OK for first image
    HoughCircles(closing,coin,CV_HOUGH_GRADIENT,1,100,1000,20,10,max_radius);
    // Argument 1: Input image mode
    // Argument 2: A vector that stores 3 values: x,y and r for each circle.
    // Argument 3: CV_HOUGH_GRADIENT: Detection method.
    // Argument 4: The inverse ratio of resolution.
    // Argument 5: Minimum distance between centers.
    // Argument 6: Upper threshold for Canny edge detector.
    // Argument 7: Threshold for center detection.
    // Argument 8: Minimum radius to be detected. Put zero as default
    // Argument 9: Maximum radius to be detected. Put zero as default

    int l=coin.size();
    // Get the number of coins.

    cout<<"\n The number of coins is: "<<l<<"\n\n";

    // To draw the detected circles.

    vector<Mat> coin_roi(coin.size());

    for( size_t i = 0; i < coin.size(); i++ )
    {
      Point center(cvRound(coin[i][0]),cvRound(coin[i][1]));
      // Detect center
      // cvRound: Rounds floating point number to nearest integer.
      int radius = cvRound(coin[i][2]);
      // To get the radius from the second argument of vector coin.

      coin_roi[i] = image(Rect(center.x - radius, center.y - radius, radius * 2, radius * 2));
      namedWindow("Coin Crop", WINDOW_NORMAL);
      imshow("Coin Crop", coin_roi[i]);
      waitKey(0);

      circle(image,center,3,Scalar(0,255,0),-1,8,0);
          // circle center
          //  To get the circle outline.
      circle(image,center,radius,Scalar(0,0,255),3,8,0);
          // circle outline
      cout<< " Center location for circle "<<i+1<<" : "<<center<<"\n Diameter : "<<2*radius<<"\n";
    }
    cout<<"\n";

    // -------------- OUTPUT ---------------

    namedWindow("Coin Counter", WINDOW_NORMAL);
    // Create a window called
    //"A_good_name".
    // first argument: name of the window.
    // second argument: flag- types:
    // WINDOW_NORMAL : The user can resize the window.
    // WINDOW_AUTOSIZE : The window size is automatically adjusted to fit the
     // displayed image() ), and you cannot change the window size manually.
    // WINDOW_OPENGL : The window will be created with OpenGL support.

    imshow("Coin Counter", image);
    // first argument: name of the window
    // second argument: image to be shown(Mat object)

    waitKey(0); // Wait for infinite time for a key press.

    return 0;    // Return from main function.
}
