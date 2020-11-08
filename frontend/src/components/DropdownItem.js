import React, { useState, useEffect } from 'react';
import PropTypes from 'prop-types';
import axios, { CancelToken } from 'axios';
import { motion } from 'framer-motion';
import DropdownSubItem from './DropdownSubItem';
import { getSubcategoriesUrl } from '../constants';
import logo from '../assets/loading.svg';


const DropdownItem = React.memo((props) => {
  const { option, handleClick } = props;
  const [isOpen, setIsOpen] = useState(false);
  const [subItems, setSubItems] = useState([]);
  const [Loading, setLoading] = useState(false);
  const variants = {
    rotateOpen: {
      rotate: [0, 90],
      transition: { duration: 0.4 }
    },
    rotateClose: {
      rotate: [90, 0],
      transition: { duration: 0.4 }
    },
  };

  useEffect(() => {
    const source = CancelToken.source();

    const fetchSubcategories = async (category) => {
      const url = `${getSubcategoriesUrl}/${category}`

      try {
        const response = await axios.get(
          url,
          { cancelToken: source.token }
        );

        setSubItems(response.data);
        setLoading(false);

      } catch(e) {
        console.log(e);
      }
    };

    if (isOpen && subItems.length === 0 && option.slug) {
      setLoading(true);
      fetchSubcategories(option.slug);
    }

    return () => {
      source.cancel('Query was cancelled');
      setLoading(false);
    };

  }, [isOpen, option, subItems])


  return (
    <div className="cursor-pointer bg-white text-gray-600 transition duration-200 hover:bg-gray-600 hover:text-white">
      <a
        href={`${option.slug}`}
        onClick={e => {
          e.preventDefault();
          setIsOpen(!isOpen);
        }}
        className="block py-2 text-md font-semibold w-full whitespace-no-wrap"
      >
        <motion.i
          className="mx-4 my-2 fas fa-chevron-right"
          variants={variants}
          animate={isOpen ? 'rotateOpen' : 'rotateClose'}
        >
        </motion.i>
        {option.name}
      </a>
      <div
        className={(isOpen ? "block" : "hidden")}
      >
        {Loading
          ? (
            <div className="p-2 font-semibold bg-white text-gray-600">
              <img src={logo} alt={'loading'} />
            </div>)
          : (subItems.map(item => (
            <DropdownSubItem
              key={item.slug}
              option={item}
              handleClick={handleClick}
            />))
        )}
      </div>
    </div>
  );
})

DropdownItem.propTypes = {
  option: PropTypes.object.isRequired,
  handleClick: PropTypes.func.isRequired
}

export default DropdownItem;
