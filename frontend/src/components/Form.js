import React, { useState, useContext } from 'react';
import { useHistory } from 'react-router-dom';
import Input from './Input';
import Dropdown from './Dropdown';
import { ModalContext } from '../context';


export default function Form() {
  const { setModal } = useContext(ModalContext);
  
  const [category, setCategory] = useState(null);
  const [inputUrl, setInputUrl] = useState('')
  const [openTab, setOpenTab] = useState(1);
  let history = useHistory();

  function validateInput(input) {
    console.log(input);
  }

  function handleClick(e) {
    e.preventDefault();

    if (openTab === 1) {
      console.log('button pushed with search-by-url');
      validateInput(inputUrl);
      const id = inputUrl || null;
      setModal(id);
      setInputUrl('');

    } else if (openTab === 2) {
      // category from API.Context
      console.log('button pushed with select-category');
      if ( category ) { 
        history.push(`/categories/${category}`);
      };
      setCategory(null);
    };
  };

  return (
      <div className="relative container mx-auto w-11/12 md:w-8/12 shadow-lg rounded-lg bg-gray-100 my-8">
        <div className="flex flex-wrap">
          <div className="w-full">
          
            {/* Tabs buttons Section */}
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
                  href="search-by-url"
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
                  href="select-category"
                  role="tablist"
                >
                  Select Category
                </a>
              </li>
            </ul>
            {/* Tabs buttons Section Ends */}

            {/* Form Section */}
              <div className="px-4 py-4">
                <div className="tab-content tab-space">
                  <div className={openTab === 1 ? "block" : "hidden"} id="link1">
                    <Input value={inputUrl} changeValue={setInputUrl} />
                  </div>
                  <div className={openTab === 2 ? "block" : "hidden"} id="link2">
                    <Dropdown category={category} changeCategory={setCategory} />
                  </div>
                </div>
              </div>
            {/* Text Section End */}

            {/* Button Section */}
            <div className="flex md:justify-center text-center">
              <button
                className="block w-11/12 justify-center bg-red-500 text-white text-md font-semibold uppercase rounded w-full py-2 mx-2 mb-2 shadow transition duration-300 hover:shadow-outline"
                onClick={e => handleClick(e)}
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