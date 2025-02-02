﻿using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;

namespace SentimentAnalyzer
{
    public partial class LoginForm : Form
    {
        public LoginForm()
        {
            InitializeComponent();
        }

        private void loginButton_Click(object sender, EventArgs e)
        {
            if (UsernameBox.Text.Length > 0 && PasswordBox.Text.Length > 0)
            {
                if (Login.AttemptLogin(UsernameBox.Text, PasswordBox.Text))
                {
                    Close();
                }
                else
                {
                    resultLabel.Text = "ERR: Invalid user or pswd";
                }
            }
        }

        private void createAcctButt_Click(object sender, EventArgs e)
        {
            if (UsernameBox.Text.Length > 0 && PasswordBox.Text.Length > 0)
            {
                if (Login.CreateAccount(UsernameBox.Text, PasswordBox.Text))
                {
                    Close();
                }
                else
                {
                    resultLabel.Text = "ERR: User Exists";
                }
            }
        }
    }
}
