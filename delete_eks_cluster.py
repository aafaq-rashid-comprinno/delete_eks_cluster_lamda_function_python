import boto3
import os
import json

def lambda_handler(event, context):
    # Set the AWS region
    #region = os.environ['Region']
    regions = [ "us-east-1", "us-west-1", "ap-south-1"]
    # global variable
    message = ""
    for region in regions:
        message = message + f'{region}: '

        # Create clients for the EKS, EC2, and ELBv2 services
        context.eks_client = boto3.client('eks', region_name=region)   
        
        # List all EKS clusters
        clusters = context.eks_client.list_clusters()["clusters"]
        print(f"Listed Clusters in {region}:\n{clusters}")
        message = message +  f"Listed Clusters in {region}:\n{clusters}"

        # Iterate over the clusters
        for cluster in clusters:

            # Get the cluster name
            cluster_name = cluster
            try:
                # Get the list of tags for the EKS cluster
                response = context.eks_client.describe_cluster(name=cluster_name)
                tags = response['cluster']['tags']

                # Check if the cluster has any tags
                if not tags:
                    # Get the list of nodes in the cluster
                    response = context.eks_client.list_nodegroups(clusterName=cluster_name)
                    nodegroups = response['nodegroups']

                    # Get the list of Fargate profiles for the cluster
                    response = context.eks_client.list_fargate_profiles(clusterName=cluster_name)
                    profiles = response['fargateProfileNames']

                    if (len(nodegroups) == 0) and (len(profiles) == 0 ):
                        try:
                            response = context.eks_client.delete_cluster(name=cluster_name)
                            print(response)
                            print(f"Cluster {cluster_name} has been terminated.")
                            message = message + f"\nCluster {cluster_name} has been terminated."
                  
                        except Exception as e:
                            print(f'Error deleting Eks Cluster {cluster_name}: {e}')
                            message = message + f'Error deleting Eks Cluster {cluster_name}: {e}'
                    else:
                        print(f'Error deleting Eks Cluster {cluster_name}: {e}')
                        message = message + f'Error deleting Eks Cluster {cluster_name}: {e}'  
                           
                   
                else:
                    print(f'Cluster {cluster_name} has tags, So resources from cluster {cluster_name} are not being deleted...')
                    message = message + f'Cluster {cluster_name} has tags, So resources from cluster {cluster_name} are not being deleted...'
                    return {
                        'message' :json.dumps(message, default=str)
                    }

            except Exception as e:
                # Print the error message if there is a problem
                print(f'Error deleting resources from cluster {cluster_name}: {e}')
                message = message + f'Error deleting resources from cluster {cluster_name}: {e}'
                return {
                    'message' :json.dumps(message, default=str)
                }
    return {
        'message' :json.dumps(message, default=str)
    }




        