import streamlit as st
from orm.functions import change_password, delete_all_messages
from utils.vanna_calls import (train_file, train_ddl, setup_vanna)

# Get the current user ID from session state cookies
user_id = st.session_state.cookies.get("user_id")
vn = setup_vanna()
df =vn.get_training_data()

def delete_all_training():
    try:
        training_data = vn.get_training_data()
        for index, row in training_data.iterrows():
            vn.remove_training_data(row["id"])
        st.toast("Training Data Deleted Successfully!")
    except Exception as e:
        st.error(f"An error occurred: {e}")
        print(e)

@st.dialog("Cast your vote")
def pop_train(type):
    try:
        if(type == "sql"):
            with st.form("add_training_data"):
                question = st.text_input("Question")
                content1 = st.text_input("Sql")
                if st.form_submit_button("Add"):
                    if question == "" or content1 == "":
                        st.error("Please fill all fields.")
                    else:
                        vn.train(question=question, sql=content1)
                        st.toast("Training Data Added Successfully!")
                        st.rerun()
        else:
            with st.form("add_training_data"):
                content2 = st.text_input("Documentation")
                if st.form_submit_button("Add"):
                    if content2 == "":
                        st.error("Please fill all fields.")
                    else:
                        vn.train(documentation=content2)
                        st.toast("Training Data Added Successfully!")
                        st.rerun()
    except Exception as e:
        st.error(f"An error occurred: {e}")
        print(e)

st.title("User Settings")

tab1, tab2 = st.tabs(["Training Data", "Change Password"])

with tab1:
    cols = st.columns((.2, .2, .2, .4, .3))
    with cols[0]:
        st.button("Train DDL", on_click=lambda: train_ddl())
    with cols[1]:
        st.button("Train FIle", on_click=lambda: train_file())
    with cols[2]:
        if(st.button("Add Sql")):
            pop_train("sql")
    with cols[3]:
        if(st.button("Add Documentation")):
            pop_train("documentation")
    with cols[4]:
        st.button("Remove All", type='primary', on_click=lambda: delete_all_training())
    
    # st.dataframe(df)

    colms = st.columns((1, 2, 3, 1))
    fields = ["Type", "Question", 'Sql', "Action"]
    for col, field_name in zip(colms, fields):
        # header
        col.write(field_name)

    for index, row in df.iterrows():
        col1, col2, col3, col4 = st.columns((1, 2, 3, 1))
        col1.write(row['training_data_type'])
        col2.write(row['question'])
        col3.write(row['content'])
        button_phold = col4.empty() 
        do_action = button_phold.button(label="Delete", type='primary', key=f"delete{row['id']}")
        if do_action:
            vn.remove_training_data(row['id'])
            st.toast("Training Data Deleted Successfully!")
            st.rerun()
with tab2:
    with st.form("change_password_form"):
        current_password = st.text_input("Current Password", type="password")
        new_password = st.text_input("New Password", type="password")
        confirm_new_password = st.text_input("Confirm New Password", type="password")
        submit_button = st.form_submit_button("Change Password")

        if submit_button:
            if new_password != confirm_new_password:
                st.error("New password and confirmation do not match.")
            else:
                if change_password(user_id, current_password, new_password):
                    st.success("Password changed successfully.")
                else:
                    st.error("Current password is incorrect.")

st.sidebar.button("Delete all message data", on_click=lambda: delete_all_messages(), use_container_width=True, type="primary")