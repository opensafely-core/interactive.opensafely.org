import { SelectorIcon, XIcon } from "@heroicons/react/solid";
import { useCombobox } from "downshift";
import { arrayOf, func, shape, string } from "prop-types";
import { useState } from "react";
import { classNames } from "./utils";

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

export function Combobox({
  choices,
  data,
  errors,
  handleSelectedItemChange,
  selectedItem,
}) {
  // Remove the first blank option and store in React state
  const comboboxChoices = choices.filter((el, i) => i > 0);
  const [inputItems, setInputItems] = useState(comboboxChoices);

  const {
    getComboboxProps,
    getInputProps,
    getItemProps,
    getLabelProps,
    getMenuProps,
    getToggleButtonProps,
    highlightedIndex,
    isOpen,
    openMenu,
    selectItem,
  } = useCombobox({
    // Use the above state reducer function
    stateReducer,
    // Set the initial items to match the choices passed as a prop
    items: inputItems,
    // Display the item label as a string to the user
    itemToString: (item) => (item ? item.label : ""),
    // Set the selected item from the props
    selectedItem,
    // When the selected item changes, run the function passed in via props
    onSelectedItemChange: handleSelectedItemChange,
    // When the input value changes, convert the value and choices to
    // lowercase, and find matching values
    onInputValueChange: ({ inputValue }) => {
      setInputItems(
        comboboxChoices.filter((item) =>
          item.label.toLowerCase().includes(inputValue.toLowerCase())
        )
      );
    },
  });

  return (
    <>
      <label
        {...getLabelProps()}
        className="block mb-1 text-lg font-semibold text-slate-800"
      >
        {/* Display the label passed in via data-label attribute */}
        {data.label}
      </label>
      <div className="relative">
        <div className="relative" {...getComboboxProps()}>
          <input
            className="block w-full pl-3 pr-10 py-2 cursor-default border border-slate-300 rounded-md shadow-sm placeholder-slate-400 focus:outline-none focus:ring-oxford-500 focus:border-oxford-500 sm:text-sm"
            required
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
              <XIcon className="h-5 w-5 text-gray-400" />
            </button>
          ) : (
            <button
              {...getToggleButtonProps()}
              aria-label="Show dropdown"
              className="absolute inset-y-0 right-0 flex items-center rounded-r-md px-2 focus:outline-none"
              tabIndex={-1}
              type="button"
            >
              <SelectorIcon className="h-5 w-5 text-gray-400" />
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
        {/* When the user selects a codelist, allow them to view it on the
         *  Codelists website.
         */}
        {selectedItem ? (
          <ul className="text-sm mt-2 list-disc pl-4">
            <li>
              <a
                className="text-oxford-600 font-semibold underline underline-offset-1 transition-colors hover:text-oxford-700 hover:no-underline focus:text-oxford-900 focus:no-underline"
                rel="noopener noreferrer"
                target="_blank"
                href={`https://www.opencodelists.org/codelist/${selectedItem.value}`}
              >
                View “{selectedItem.label}” codelist &#8599;
              </a>
            </li>
          </ul>
        ) : null}
        {/* Display errors passed as a data attribute */}
        {errors?.length ? (
          <ul className="mt-2">
            <li className="text-sm text-red-700">
              {errors}
            </li>
          </ul>
        ) : null}

        {/* Display the hint text passed as a data attribute */}
        <p className="text-slate-600 text-sm pt-2">{data.hint}</p>
      </div>

      {/* Show a section below the Combobox explaining about codelists */}
      <div className="border-l-2 border-l-oxford-200 bg-oxford-50 rounded pl-4 pr-2 py-4 mt-4 text-sm text-slate-800">
        <ul className="list-disc pl-4 grid grid-flow-row gap-2">
          <li>
            <a
              className="text-oxford-600 font-semibold underline underline-offset-1 transition-colors hover:text-oxford-500 hover:no-underline focus:text-oxford-700 focus:no-underline"
              href="https://www.opencodelists.org/docs/#what-is-a-codelist"
              rel="noopener noreferrer"
              target="_blank"
            >
              What is a codelist?
            </a>
          </li>
          <li>
            <a
              className="text-oxford-600 font-semibold underline underline-offset-1 transition-colors hover:text-oxford-500 hover:no-underline focus:text-oxford-700 focus:no-underline"
              href="https://www.snomed.org/"
              rel="noopener noreferrer"
              target="_blank"
            >
              What is SNOMED CT?
            </a>
          </li>
        </ul>
      </div>
    </>
  );
}

Combobox.propTypes = {
  choices: arrayOf(
    shape({
      value: string,
      label: string,
    }).isRequired
  ),
  data: shape({
    choices: string,
    errors: string,
    hint: string,
    id: string,
    label: string,
    name: string,
  }).isRequired,
  errors: arrayOf(string),
  handleSelectedItemChange: func.isRequired,
  selectedItem: shape({
    value: string,
    label: string,
  }),
};

Combobox.defaultProps = {
  errors: null,
  selectedItem: null,
};
