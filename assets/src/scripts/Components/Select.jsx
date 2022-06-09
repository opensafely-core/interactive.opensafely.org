import { arrayOf, shape, string } from "prop-types";
import { useState } from "react";
import { Combobox } from "./Combobox";

export function Select({ choices, data, errors }) {
  // Initialise the form with no item selected
  const [selectedItem, setSelectedItem] = useState(null);
  function handleSelectedItemChange({ selectedItem }) {
    setSelectedItem(selectedItem);
  }

  return (
    <>
      {/* Render the Combobox component */}
      <Combobox
        choices={choices}
        data={data}
        errors={errors}
        selectedItem={selectedItem}
        handleSelectedItemChange={handleSelectedItemChange}
      />

      {/* Render an HTML select component,
       *  hidden from view so that Django can read the value.
       *
       *  Update the value based on the state,
       *  or display the default option.
       */}
      <select
        id={data.id}
        name={data.name}
        readOnly
        value={selectedItem ? selectedItem.value : "---"}
        hidden
      >
        {choices.map((item) => (
          <option key={item.value} value={item.value}>
            {item.label}
          </option>
        ))}
      </select>
    </>
  );
}

Select.propTypes = {
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
  errors: arrayOf(string).isRequired,
};
