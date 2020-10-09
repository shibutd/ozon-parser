import React, { useState } from 'react';
import Dropdown from './Dropdown';


export default function Form() {
const [openTab, setOpenTab] = useState(1)

  return (
      <div className="relative container mx-auto w-11/12 md:w-8/12 shadow-lg rounded-lg bg-gray-100 my-8">
        <div className="flex flex-wrap">
          <div className="w-full">
          
            {/* Buttons Section */}
            <ul className="flex list-none flex-wrap flex-row" role="tablist">
              <li className="text-center flex-auto">
                <a
                  className={
                    "font-semibold uppercase px-3 py-3 shadow transition duration-300 hover:shadow-lg rounded block leading-normal " +
                    (openTab === 1
                    ? "text-white bg-red-500"
                    : "text-red-500 bg-white")
                  }
                  onClick={e => {
                    e.preventDefault();
                    setOpenTab(1);
                  }}
                  data-toggle="tab"
                  href="#link1"
                  role="tablist"
                >
                  Search by URL
                </a>
              </li>
              <li className="text-center flex-auto">
                <a
                  className={
                    "font-semibold uppercase px-3 py-3 shadow transition duration-300 hover:shadow-lg rounded block leading-normal " +
                    (openTab === 2
                    ? "text-white bg-red-500"
                    : "text-red-500 bg-white")
                  }
                  onClick={e => {
                    e.preventDefault();
                    setOpenTab(2);
                  }}
                  data-toggle="tab"
                  href="#link2"
                  role="tablist"
                >
                  Select Category
                </a>
              </li>
            </ul>
            {/* Buttons Section Ends */}

            {/* Form Section */}
              <div className="px-4 py-4">
                <div className="tab-content tab-space">
                  <div className={openTab === 1 ? "block" : "hidden"} id="link1">
                    <input
                      type="text"
                      className="px-3 py-3 placeholder-gray-500 placeholder-opacity-50 text-black bg-white rounded tracking-wider text-md w-full shadow-md focus:outline-none focus:shadow-outline"
                      placeholder="https://ozon.ru/context/item/id/5151551/"
                      style={{ transition: "all .15s ease" }}
                    />

                  </div>
                  <div className={openTab === 2 ? "block" : "hidden"} id="link2">
                    <Dropdown />
                  </div>
                </div>
              </div>
            {/* Text Section End */}

            {/* Button Section */}
            <div className="flex md:justify-center text-center">
              <button
                className="block w-11/12 justify-center bg-red-500 text-white text-md font-semibold uppercase rounded w-full py-2 mx-2 mb-2 shadow transition duration-300 hover:shadow-outline "
                type="button"
              >
                Search
              </button>
            </div>
            {/* Button Section End */}

          </div>
        </div>
      </div>
  );
}