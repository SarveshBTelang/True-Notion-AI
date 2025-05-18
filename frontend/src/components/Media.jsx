import videoFile from '../icons/data_ingestion.mp4';
import imageFile1 from '../icons/features.png';

const VideoImageDisplay = () => {
  return (
    <div className="flex flex-col lg:flex-row gap-20 px-4 py-8">
      {/* Video Box - Hidden on small screens */}
      <div className="hidden lg:block border-2 border-gray-350 rounded-xl shadow-2xl p-2 flex w-full max-w-[1000px] h-[600px]">
        <video autoPlay loop muted className="w-full h-full object-cover rounded-md">
          <source src={videoFile} type="video/mp4" />
          Your browser does not support the video tag.
        </video>
      </div>

      {/* Image1 Box */}
      <div className="border-2 border-gray-350 rounded-xl shadow-2xl p-2 flex justify-center items-center
                      h-[700px] sm:h-[700px] md:h-[700px] lg:h-[800px] max-h-[800px]">
        <img
          src={imageFile1}
          alt="Example"
          className="h-full w-auto object-contain rounded-md"
        />
      </div>
    </div>
  );
};

export default VideoImageDisplay;
