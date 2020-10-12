import React, { useState, createContext } from 'react';
import PropTypes from "prop-types";


export const ModalContext = createContext();

export function AppContextProvider(props) {
  const [modal, setModal] = useState(null);
  const modalStore = {modal: modal, setModal: setModal}

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
