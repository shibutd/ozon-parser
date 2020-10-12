import React from 'react';
import PropTypes from 'prop-types';

export default function InfoTab(props) {
  const { color, icon, title, msg } = props;
  return (
    <div className="relative flex flex-col min-w-0 break-words bg-white w-full mb-8 shadow-lg rounded-lg transition duration-300 transform hover:scale-102">
      <div className="px-4 py-5 flex-auto">
        <div 
          className={
            "text-white p-3 text-center inline-flex items-center justify-center w-12 h-12 mb-5 shadow-lg rounded-full " + color
          }
        >
          <i className={icon}></i>
        </div>
        <h6 className="text-xl font-semibold">
          {title}
        </h6>
        <p className="mt-2 mb-4 text-gray-600 italic">
          {msg}
        </p>
      </div>
    </div>
  )
}

InfoTab.propTypes = {
  color: PropTypes.string,
  icon: PropTypes.string,
  title: PropTypes.string,
  msg: PropTypes.string,
}
