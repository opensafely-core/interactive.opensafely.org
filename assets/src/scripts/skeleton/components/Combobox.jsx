import { ChevronUpDownIcon, XMarkIcon } from "@heroicons/react/20/solid";
import { useCombobox } from "downshift";
import React, { useState } from "react";
import { classNames } from "../utils";

/**
 * Utilise a reducer to revert the users selection if they
 * backspace on the input, but do not select a new option.
 */
function stateReducer(state, actionAndChanges) {
  const { type, changes } = actionAndChanges;
  switch (type) {
    case useCombobox.stateChangeTypes.InputChange:
      return {
        ...changes, // return normal changes.
      };
    case useCombobox.stateChangeTypes.InputBlur:
      return {
        ...changes,
        // if we had an item selected...
        ...(changes.selectedItem && {
          // revert changes to the selected label
          inputValue: changes.selectedItem.label,
        }),
      };
    default:
      return changes; // otherwise business as usual.
  }
}

function Combobox({
  choices,
  label,
  name,
  setFieldValue,
  initialSelectedItem,
  placeholder,
}) {
  const comboboxChoices = choices.filter((el, i) => i > 0);
  const [inputItems, setInputItems] = useState(comboboxChoices);

  const {
    getInputProps,
    getItemProps,
    getLabelProps,
    getMenuProps,
    getToggleButtonProps,
    highlightedIndex,
    isOpen,
    openMenu,
    selectedItem,
    selectItem,
  } = useCombobox({
    // Use the above state reducer function
    stateReducer,
    // Set the initial items to match the choices passed as a prop
    items: inputItems,
    // Display the item label as a string to the user
    itemToString: (item) => (item ? item.label : ""),
    // When the selected item changes, set the combobox and data store
    onSelectedItemChange: (e) => {
      setFieldValue([name], e.selectedItem);
    },
    // When the input value changes, convert the value and choices to
    // lowercase, and find matching values
    onInputValueChange: ({ inputValue }) => {
      setInputItems(
        comboboxChoices.filter((item) =>
          item.label.toLowerCase().includes(inputValue.toLowerCase())
        )
      );
    },
    // Set the initial item on page change
    initialSelectedItem,
  });

  return (
    <>
      <label {...getLabelProps()} className="sr-only">
        {/* Display the label passed in via data-label attribute */}
        {label}
      </label>
      <div className="relative">
        <div className="relative">
          <input
            className="block w-full pl-3 pr-10 py-2 cursor-default border border-slate-300 rounded-md shadow-sm placeholder-slate-400 focus:outline-none focus:ring-oxford-500 focus:border-oxford-500 sm:text-sm"
            // required
            placeholder={placeholder}
            {...getInputProps({
              // Automatically open the menu when the input is focussed
              onFocus: () => {
                if (!isOpen) {
                  openMenu();
                }
              },
            })}
          />
          {/* If an item has been selected, show a button to clear the
           *  selection, otherwise show a button to allow the user to open the
           *  choices list.
           *
           *  These buttons are not keyboard accessible, as focusing the input
           *  will open the menu.
           */}
          {selectedItem ? (
            <button
              aria-label="Clear selection"
              className="absolute inset-y-0 right-0 flex items-center rounded-r-md px-2 focus:outline-none"
              onClick={() => {
                setInputItems(comboboxChoices);
                selectItem(null);
              }}
              tabIndex={-1}
              type="button"
            >
              <XMarkIcon className="h-5 w-5 text-gray-400" />
            </button>
          ) : (
            <button
              {...getToggleButtonProps()}
              aria-label="Show dropdown"
              className="absolute inset-y-0 right-0 flex items-center rounded-r-md px-2 focus:outline-none"
              tabIndex={-1}
              type="button"
            >
              <ChevronUpDownIcon className="h-5 w-5 text-gray-400" />
            </button>
          )}
        </div>
        <div {...getMenuProps({})}>
          {/* Display the menu when the Downshift state is configured to open.
           *
           *  Map over the items if they exist, otherwise display a message to
           *  the user that they need to modify their search.
           */}
          {isOpen ? (
            <ul
              aria-label="Select a codelist"
              className="absolute z-10 mt-1 max-h-60 w-full overflow-auto rounded-md bg-white py-1 text-base shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none sm:text-sm"
            >
              {inputItems.length ? (
                <>
                  {/* Map over the items and visually identify the highlighted
                   *  or selected options.
                   */}
                  {inputItems.map((item, index) => (
                    <li
                      {...getItemProps({
                        item,
                        index,
                        key: item.value,
                        className: classNames(
                          selectedItem === item && "bg-oxford-100 font-bold",
                          highlightedIndex === index && "bg-gray-100",
                          "flex flex-col relative cursor-pointer select-none py-2 pl-3 pr-9  font-semibold text-oxford-600 hover:bg-gray-100"
                        ),
                      })}
                    >
                      {item.label}
                      <span className="sr-only">, </span>
                      <span className="text-xs text-gray-600 font-normal">
                        From: {item.organisation}
                      </span>
                    </li>
                  ))}
                </>
              ) : (
                <li className="relative cursor-not-allowed select-none py-2 pl-3 pr-9 text-gray-900">
                  No codelists available your query
                </li>
              )}
            </ul>
          ) : null}
        </div>
      </div>
    </>
  );
}

export default Combobox;
