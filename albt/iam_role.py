from __future__ import absolute_import
from .printmsg import PrintMsg
import boto3
import json
from botocore.exceptions import ClientError


class IamRole(object):
    """
    Iam Role
    Create and update roles
    """
    def __init__(self, debug=False, profile=None):
        """
        Init
        :param debug:
        """
        self.debug = debug
        self.profile = profile
        if self.profile:
            boto3.setup_default_session(profile_name=self.profile)
        PrintMsg.debug = self.debug
        self.client = boto3.client('iam')

    def create(self, name, desc, policy, path=None):
        """
        Create Iam Role
        :param name:
        :param desc:
        :param policy:
        :param path:
        :return:
        """
        PrintMsg.creating('{} Role'.format(name))
        return self.__create__(name, desc, policy, path)

    def update(self, name, policy, desc=None):
        """
        Update Iam role
        :param name:
        :param policy:
        :param desc:
        :return:
        """
        PrintMsg.updating('{} Role'.format(name))
        return self.__update__(name, policy, desc)

    def create_policy(self, name, desc, policy, account_id=None, path=None):
        """
        Create Policy
        :param name:
        :param desc:
        :param policy:
        :param account_id:
        :param path:
        :return:
        """
        return self.__create_policy__(name, desc, policy, account_id, path)

    def attach_policy(self, role_name, policy_arn):
        """
        Attach Policy
        :param role_name:
        :param policy_arn:
        :return:
        """
        return self.__attach_policy__(role_name, policy_arn)

    def __attach_policy__(self, role_name, policy_arn):
        """
        Attach an iam policy to a role
        :param role_name:
        :param policy_arn:
        :return:
        """
        response = self.client.attach_role_policy(
            RoleName=role_name,
            PolicyArn=policy_arn
        )

        PrintMsg.out(response)
        PrintMsg.cmd('Policy', 'ATTACHED')
        return True

    def __create_policy__(self, name, desc, policy, account_id=None, path=None):
        """
        Create iam policy
        :param name:
        :param desc:
        :param policy:
        :param account_id:
        :param path:
        :return:
        """
        policy = json.dumps(policy)

        try:
            if path:
                response = self.client.create_policy(
                    PolicyName=name,
                    Path=path,
                    PolicyDocument=policy,
                    Description=desc
                )
            else:
                response = self.client.create_policy(
                    PolicyName=name,
                    PolicyDocument=policy,
                    Description=desc
                )
        except ClientError as e:
            PrintMsg.out(e)
            if account_id:
                policy_arn = "arn:aws:iam::{}:policy/{}".format(account_id, name)
                response = self.client.get_policy(
                    PolicyArn=policy_arn
                )
                PrintMsg.out(response)
            else:
                response = None
        if 'Policy' in response:
            PrintMsg.cmd('Policy', 'CREATED')
            return response['Policy']
        else:
            PrintMsg.error('Failed to create policy')
            return None

    def __update__(self, name, policy, desc=None):
        """
        Update iam role policy optionally description
        :param name:
        :param policy:
        :param desc:
        :return:
        """
        policy = json.dumps(policy)
        response = self.client.update_assume_role_policy(
            RoleName=name,
            PolicyDocument=policy
        )
        if desc:
            response = self.client.update_role_description(
                RoleName=name,
                Description=desc
            )

        if 'Role' in response:
            PrintMsg.out(response)
            PrintMsg.cmd('Role', 'UPDATED')
            return response['Role']
        else:
            PrintMsg.error('Failed to update policy')
            return None

    def __create__(self, name, desc, policy, path=None):
        """
        Create an iam role
        Path is an optional parameter
        :param name:
        :param desc:
        :param policy:
        :param path:
        :return:
        """

        policy = json.dumps(policy)

        try:
            if path:
                response = self.client.create_role(
                    Path=path,
                    RoleName=name,
                    AssumeRolePolicyDocument=policy,
                    Description=desc
                )
            else:
                response = self.client.create_role(
                    RoleName=name,
                    AssumeRolePolicyDocument=policy,
                    Description=desc
                )
        except ClientError as e:
            PrintMsg.out(e)
            response = self.client.get_role(
                RoleName=name
            )

        PrintMsg.out(response)
        if 'Role' in response:
            PrintMsg.cmd(name, 'CREATED')
            return response['Role']
        else:
            PrintMsg.error('Failed to create role')
            return None
