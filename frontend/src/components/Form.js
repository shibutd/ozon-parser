import React, { useState, useContext } from 'react';
import { useHistory } from 'react-router-dom';
import { useQuery } from 'react-query';
import axios, { CancelToken } from 'axios';
import Input from './Input';
import Dropdown from './Dropdown';
import { ModalContext } from '../context';
import { getCategoriesUrl } from '../constants';


async function fetchCategories() {
  const source = CancelToken.source()

  const promise = await axios.get(getCategoriesUrl, {
    cancelToken: source.token,
  });

  promise.cancel = () => {
    source.cancel('Query was cancelled')
  };
 
  return promise.data;
}

export default function Form() {
  const patternId = /^(.*)?(\d{9,})\/?$/;
  const patternUrl = /^((https?):\/\/)?(www\.)?ozon\.ru(\/.*)?$/
  const { setModal } = useContext(ModalContext);
  const [category, setCategory] = useState('');
  const [inputUrl, setInputUrl] = useState('');
  const [error, setError] = useState('');
  const [openTab, setOpenTab] = useState(1);
  let history = useHistory();
  const { data, status } = useQuery('categories', fetchCategories, {
    staleTime: 6000,
    cachedTime: 60000,
    refetchOnWindowFocus: false,
  });

  function handleChangeInput(e) {
    setInputUrl(e.target.value);
    setError('');
  };

  function validateId(value) {
    return patternId.test(value);
  };

  function validateUrl(value) {
    return patternUrl.test(value);
  };

  function validateInput(input) {
    if (!input) {
      return { isValid: false, error: "Enter product's page URL or product's ID" }

    } else if (validateUrl(input) && !validateId(input)) {
      return { isValid: false, error: "URL should contain product's ID" }
    
    } else if (!validateUrl(input) && !validateId(input)) {
      return { isValid: false, error: "ID should consists of 9 or more digits" }
    }
    return { isValid: true, error: "" }
  };

  function handleClick(e) {
    e.preventDefault();

    if (openTab === 1) {
      const inputIsValid = validateInput(inputUrl);

      if (inputIsValid.isValid) {
        const itemId = inputUrl.match(patternId)[2];
        setModal(itemId);
      } else {
        setError(inputIsValid.error);
      }

    } else if (openTab === 2) {
      if ( category ) { 
        history.push(`/categories/${category}`);
      };
      setCategory('');
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
            {/* Tabs buttons Section End */}

            {/* Input Section */}
              <div className="px-4 py-4">
                <div className="tab-content tab-space">
                  <div className={openTab === 1 ? "block" : "hidden"} id="link1">
                    <Input
                      value={inputUrl}
                      handleChange={handleChangeInput}
                      error={error}
                    />
                  </div>
                  <div className={openTab === 2 ? "block" : "hidden"} id="link2">
                    <Dropdown
                      options={{ data: data, status: status}}
                      category={category}
                      changeCategory={setCategory}
                    />
                  </div>
                </div>
              </div>
            {/* Input Section End */}

            {/* Button Section */}
            <div className="flex md:justify-center text-center">
              <button
                className="block w-11/12 justify-center bg-red-500 text-white text-md font-semibold uppercase rounded w-full py-2 mx-2 mb-2 shadow focus:outline-none transition duration-300 hover:shadow-outline"
                onClick={handleClick}
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