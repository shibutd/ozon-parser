import { useEffect } from 'react';


export function useOnClickOutside(ref, handler) {
  useEffect(() => {
    const listener = event => {
      if (!ref.current || ref.current.contains(event.target)) {
        return;
      }
      handler(event);
    };

    document.addEventListener('mousedown', listener);
    document.addEventListener('touchstart', listener);

    return () => {
      document.removeEventListener('mousedown', listener);
      document.removeEventListener('touchstart', listener);
    };
  }, [ref, handler]);
}


export function useValidateInput(input) {
  const patternId = /^(.*)?(\d{9,})\/?$/;
  const patternUrl = /^((https?):\/\/)?(www\.)?ozon\.ru(\/.*)?$/;

  function validateId(value) {
    return patternId.test(value);
  };

  function validateUrl(value) {
    return patternUrl.test(value);
  };

  function validateInput(input) {
    let validationResult = {};
    const itemId = 0;

    if (!input) {
      validationResult = {
        inputIsValid: false,
        validationMsg: "Enter product's page URL or product's ID",
        itemId: itemId
      }

    } else if (validateId(input)) {
      validationResult = {
        inputIsValid: true,
        validationMsg: "",
        itemId: input.match(patternId)[2]
      }

    } else if (validateUrl(input)) {
      const url = new URL(input);
      const urlPath = url.pathname;
      validationResult = (validateId(urlPath)
        ? {
            inputIsValid: true,
            validationMsg: "",
            itemId: urlPath.match(patternId)[2]
          }
        : {
            inputIsValid: false,
            validationMsg: "URL should contain product's ID",
            itemId: itemId
          }
      );

    } else {
      validationResult = {
        inputIsValid: false,
        validationMsg: "ID should consists of 9 or more digits",
        itemId: itemId
      }
    };

    return validationResult;
  };

  return validateInput(input);
}
