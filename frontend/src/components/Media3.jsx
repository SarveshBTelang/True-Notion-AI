import imageFile2 from '../icons/steps.png';
import imageFile3 from '../icons/truenotion_illustration.png';

const ImageDisplay = () => {
  return (
    <div className="flex flex-col lg:flex-row gap-20 px-4 py-8">
      {/* Image3 Box */}
      <div className="hidden lg:block border-2 border-gray-350 rounded-xl shadow-2xl p-2 flex w-full max-w-[1000px] h-[600px]">
          <img src={imageFile3} alt="Example" className="w-full h-full object-cover rounded-md" />
      </div>

      {/* Image2 Box */}
      <div className="border-2 border-gray-350 rounded-xl shadow-2xl p-2 flex justify-center items-center
                      h-[700px] sm:h-[700px] md:h-[700px] lg:h-[800px] max-h-[800px]">
        <img
          src={imageFile2}
          alt="Example"
          className="h-full w-auto object-contain rounded-md"
        />
      </div>
    </div>
  );
};


export default ImageDisplay;

