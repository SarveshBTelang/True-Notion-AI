import { useState } from 'react';
import { FaGithub, FaStar, FaLinkedin, FaHome } from 'react-icons/fa';
import Lottie from 'lottie-react';
import arrowAnimation from '../icons/arrow.json';

const SocialButtons = () => {
  const [showAnimation, setShowAnimation] = useState(false);

  const buttons = [
    {
      label: 'Home',
      icon: <FaHome />,
      link: 'http://localhost:3000/true-notion-ai/',
      external: false,
    },
    {
      label: 'GitHub',
      icon: <FaGithub />,
      link: 'https://github.com/SarveshBTelang/True-Notion-AI',
      external: true,
    },
    {
      label: 'Support with Star',
      icon: <FaStar />,
      link: null,  // No link because we want to handle click for animation
      external: false,
      onClick: () => {
        setShowAnimation(true);
        setTimeout(() => setShowAnimation(false), 1300);
      }
    }
  ];

  return (
    <div className="flex flex-wrap gap-1 relative">
      {buttons.map(({ label, icon, link, external, onClick }, i) => (
        <a
          key={i}
          href={link || '#'}
          onClick={e => {
            if (onClick) {
              e.preventDefault();
              onClick();
            }
          }}
          {...(external
            ? { target: '_blank', rel: 'noopener noreferrer' }
            : {})}
          className="
            group relative inline-flex 
            h-10 sm:h-12
            items-center justify-center overflow-hidden rounded-full 
            bg-transparent
            border-2 border-[#263381] dark:border-[rgb(76_100_255)] 
            mt-3 ml-3 px-4 sm:px-6
            font-medium text-white
            text-sm sm:text-base
            transition-all duration-100
            translate-x-[3px] translate-y-[3px] [box-shadow:0px_0px_rgb(38_51_129)]
            hover:translate-x-[0px] hover:translate-y-[0px] hover:[box-shadow:5px_5px_rgb(38_51_129)]
            dark:hover:[box-shadow:5px_5px_rgb(76_100_255)]
            dark:active:[box-shadow:0px_0px_rgb(76_100_255)]
            active:[box-shadow:0px_0px_rgb(38_51_129)] active:translate-y-[3px] active:translate-x-[3px]
          "
        >
          <div className="flex items-center gap-2 text-white">
            <span>{icon}</span>
            <span>{label}</span>
          </div>
        </a>
      ))}

      {/* Lottie animation overlay */}
      {showAnimation && (
        <div
          className="pointer-events-none absolute top-[8px] left-[190px] sm:top-[14px] sm:left-[230px]"
          style={{
            width: 110,
            height: 110,
            zIndex: 9999,
          }}
        >
          <Lottie
            animationData={arrowAnimation}
            loop={false}
            style={{
              width: '100%',
              height: '100%',
            }}
          />
        </div>
      )}
    </div>
  );
};

export default SocialButtons;