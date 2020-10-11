import React, { useState, useContext, createContext } from 'react';
import PropTypes from "prop-types";


export const ModalContext = createContext();

export function useModal() {
  return useContext(ModalContext)
}

export function AppContextProvider(props) {
  const [modal, setModal] = useState(null);

  const modalStore = {modal: modal, setModal: setModal}

  // useEffect(() => {
  //   fetch(getCategoriesURL)
  //     .then(response => response.json())
  //     .then(data => setCategories(data))
  //     .catch(error => console.warn(error));
  // }, [])

  // return (
  //   <CategoryContext.Provider value={category}>
  //     <ModalContext.Provider value={[modal, setModal]}>
  //       {props.children}
  //     </ModalContext.Provider>
  //   </CategoryContext.Provider>
  // );

  return (
    <ModalContext.Provider value={modalStore}>
      {props.children}
    </ModalContext.Provider>
  )
}

AppContextProvider.propTypes = {
  children: PropTypes.oneOfType([
    PropTypes.arrayOf(PropTypes.node),
    PropTypes.node
  ]).isRequired
}
